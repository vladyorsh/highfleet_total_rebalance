from parsing import *

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
    
    m_name = 'PROFILE@ยน' + ''.join([ str(np.random.randint(0, 9)) for _ in range(3)])
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