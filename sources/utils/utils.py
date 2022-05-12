from ast import literal_eval
import numpy as np
import copy

def parse_parenthesis(text):
  '''Parses a text between a pair of parenthesis on the same level and which are preceded by newlines.
  That typically denotes a single HF config object, which may recursively contain further objects.'''
  
  level = 0
  block_found = False
  parsed_string = []

  start_idx, end_idx = 0, 0
  
  for i, symbol in enumerate(text):
    
    if symbol == '{' and i < len(text) - 1 and text[i+1] == '\n':
      level += 1
      if not block_found:
        block_found = True
        start_idx = i
    elif  symbol == '}' and text[i-1] == '\n': level -= 1
    
    parsed_string.append(symbol)

    if level == 0 and block_found:
      end_idx = i + 1
      return ''.join(parsed_string), start_idx, end_idx
  
  return None

def convert_to_python_type(string):
  '''Evaluates a string containing value and parses it into a Python data type'''
  output = None
  try:
    output = literal_eval(string)
  except:
    output = string
  
  return output

def max_level(text):
  '''Checks max depth of parenthesized objects in the text'''
  level = 0
  max_level = 0
  
  for i, symbol in enumerate(text):
    
    if symbol == '{': level += 1
    elif  symbol == '}': level -= 1

    if level > max_level: max_level = level

  return max_level

def shoelace_area(mesh_object):
  '''Computes the mesh area using the Gauss' fomula'''
  X = mesh_object.num_seq[::2]
  Y = mesh_object.num_seq[1::2]

  area = 0

  for i in range(len(X)):
    area += X[i] * Y[ (i+1) % len(Y) ]
    area -= X[ (i+1) % len(X) ] * Y[i]

  area = abs(area) / 2
  return area

def compute_part_mass(part):
  mesh = part.get_children_by_name('m_mesh')[0]
  dens = part.m_density

  X, Y = mesh.num_seq[::2], mesh.num_seq[1::2]
  P = np.stack([X, Y]).T #N x 2 point table
  D = (P.max(axis=0) - P.min(axis=0)).min() #Min from width/height

  return shoelace_area(mesh) * dens * D

def generate_id(len=19):
  sign = 1 if np.random.rand() <= 0.5 else -1
  num = 0
  for dig in [ np.random.randint(0, 9) for _ in range(len) ]:
    num = num * 10 + dig
  num *= sign
  return num

def replace_escadra_ships(escadra, ship_list):
  #escadra = copy.deepcopy(escadra)

  radiation_values = []
  
  def sample_radiation_value(values):
    mean = np.mean(radiation_values)
    std  = np.std(radiation_values, ddof=-1)
    while True:
      value = np.random.randn() * std + mean
      if value > 0:
        return value

  signatures = []
  ir_signatures = []
  radar_signatures = []

  escadra_indices = []
  
  for ship in escadra.get_children_by_name('m_children'):
    creature = ship.find_by_attr('m_name', 'COMBRIDGE')[0].get_children_by_id(47)[0]
    rad = creature.m_radiation_extra if hasattr(creature, 'm_radiation_extra') else 0.0
    radiation_values.append(rad)
    
    signatures.append(creature.m_tele_signature)
    ir_signatures.append(creature.m_tele_signature_ir)
    radar_signatures.append(creature.m_tele_signature_rd)

    escadra_indices.append(creature.m_escadra_index)

  m_id = escadra.m_id
  new_ships = []
  for i, donor_ship in enumerate(ship_list):
    owner = generate_id()

    donor_ship = copy.deepcopy(donor_ship)
    donor_ship.output_order = [ item for item in donor_ship.output_order if type(item) == str or item[0][1] == 31 ]
    donor_ship.set('m_id', generate_id())
    donor_ship.set('m_master_id', m_id)
    donor_ship.set('m_state', 2)

    ########
    frame = donor_ship.get_children_by_name('m_children')[0]
    frame.output_order = [ item for item in frame.output_order if type(item) == str or item[0][0] == 'm_mesh' or (hasattr(item[1], 'm_name') and item[1].m_name == 'COMBRIDGE')  ]
    frame.set('m_master_id', donor_ship.m_id)
    frame.set('m_id', generate_id())
    #m_owner_id
    frame.set('m_owner_id', owner)
    
    frame.remove('m_center.x')
    frame.remove('m_center.y')
    
    #Prepare combridge
    combridge = frame.get_children_by_id(15)[0]
    combridge.set('m_id', generate_id())
    combridge.set('m_master_id', frame.m_id)
    #m_owner_id
    combridge.set('m_owner_id', owner)
    
    #Prepare creature
    creature = combridge.get_children_by_id(47)[0]
    
    m_name = 'PROFILE@¹' + ''.join([ str(np.random.randint(0, 9)) for _ in range(3)])
    #m_owner_id?
    creature.set('m_id', owner)
    creature.set('m_master_id', combridge.m_id)
    creature.set('m_name', m_name)
    creature.set('m_health_lock', 'true')
    creature.set('m_bio_snapshot', 'no_photo')
    creature.set('m_escadra.id', m_id)
    
    #m_alignment?
    creature.set('m_alignment', -1)
    creature.set('m_tele_parts', 3)
    creature.set('m_tele_parts_integral', 3)
    #m_escadra_index <-- ordering?
    creature.set('m_escadra_index', i+1)
    #m_radiation_extra <-- sampled based on other ship values
    creature.set('m_radiation_extra', sample_radiation_value(radiation_values))
    
    creature.remove('creatureId')
    creature.remove('m_damageCounter')
    
    #m_owner_id
    creature.set('m_owner_id', owner)
    #m_tele_fuel*
    new_ships.append(donor_ship)

  ship_index = 0
  for i, item in enumerate(escadra.output_order):
    if type(item) == tuple and item[0][0] == 'm_children':
      ship_index = i
      break

  escadra.output_order = [ item for item in escadra.output_order if type(item) == str or item[0][0] != 'm_children' ]
  escadra.output_order = escadra.output_order[:ship_index] + [ (('m_children', 7), ship) for ship in new_ships ] + escadra.output_order[ship_index:]

  #Replace escadra metadata

  return escadra