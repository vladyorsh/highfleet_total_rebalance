from .utils import *

class Node(object):
  '''General class to work with recursively nested HF config objects. Implements parsing from text,
  short (for general displaying) and full (for *.seria outputting) text representations and functions to look up
  nodes by their attributes.'''
  def __init__(self):
    self.output_order = []

  def __repr__(self):
    return str(self)

  def __str__(self):
    output_buff = '{\n'
    for item in self.output_order:
      if item == 'num_seq':
        for x in self.num_seq: output_buff += str(x) + '\n'
      elif isinstance(item, str):
        attr = item
        val  = getattr(self, attr)
        
        if not isinstance(val, list): output_buff += attr + '=' + str(val) + '\n'
        else:
          for x in val:
            output_buff += attr + '=' + str(x) + '\n'
      elif isinstance(item, tuple):
        header, node = item
        output_buff += str(header[0]) + '=' + str(header[1]) + '\n'
        output_buff += '{...}\n'
    output_buff += '}'
    return output_buff

  def output(self):
    output_buff = '{\n'
    for item in self.output_order:
      if item == 'num_seq':
        for x in self.num_seq: output_buff += str(x) + '\n'
      elif isinstance(item, str):
        attr = item
        val  = getattr(self, attr)
        
        if not isinstance(val, list): output_buff += attr + '=' + str(val) + '\n'
        else:
          for x in val:
            output_buff += attr + '=' + str(x) + '\n'
      elif isinstance(item, tuple):
        header, node = item
        output_buff += str(header[0]) + '=' + str(header[1]) + '\n'
        output_buff += node.output()
      else:
        print('Cannot parse item:', item)
        return None
    output_buff += '}\n'
    return output_buff

  def write(self, path):
    with open(path, 'w', encoding="ISO-8859-1") as f:
      f.write(self.output())

  def get_children_by_id(self, id):
    return [ item[1] for item in self.output_order if isinstance(item, tuple) and item[0][1] == id ]
  
  def get_children_by_name(self, name):
    return [ item[1] for item in self.output_order if isinstance(item, tuple) and item[0][0] == name ]

  def get_subnodes_as_list(self):
    children = [ child[1].get_subnodes_as_list() for child in self.output_order if isinstance(child, tuple) ]
    children = [ x for item in children for x in item ]
    return children + [self]

  def find_by_attr(self, attr, value=None):
    ch_found = [ child[1].find_by_attr(attr, value) for child in self.output_order if isinstance(child, tuple)  ]
    found = [ x for item in ch_found for x in item ]

    for m_attr in self.output_order:
      if isinstance(m_attr, str):
        if (m_attr == attr) and (value is None or getattr(self, attr) == value):
          found.append(self)
          break
    return found

  def get_nonchildren_attrs(self):
    return [ item for item in self.output_order if isinstance(item, str) ]

  @classmethod
  def from_file(cls, path):
    with open(path, 'r', encoding="ISO-8859-1") as f:
      text = f.read()
      node_text, _, _ = parse_parenthesis(text)
      ship = cls.parse_from_text(node_text)
    
    return ship

  def get(self, attr, def_value):
    return getattr(self, attr) if hasattr(self, attr) else def_value

  def set(self, attr, value):
    setattr(self, attr, value)
    if attr not in self.output_order:
      self.output_order.append(attr)

  def remove(self, value):
    self.output_order.remove(value)
  
  @classmethod
  def parse_from_text(cls, text):
    
    def parse_text_into_object_attrs(o, lines):
      for line in lines:
        try:
          try:
            attr, val = line.split('=')
          except:
            desc_line = line.split('=')
            if len(desc_line) < 3: raise ValueError('Passing this to num processing')
            attr, val = desc_line[0], '='.join(desc_line[1:])

          try: val = literal_eval(val)
          except: pass

          if not hasattr(o, attr):
            setattr(o, attr, val)
            o.output_order.append(attr)
          else:
            if isinstance(getattr(o, attr), list):
              attr_val = getattr(o, attr) + [ val ]
              setattr(o, attr, attr_val)
            else:
              setattr(o, attr, [ getattr(o, attr) ] + [ val ])
        except:
          try: line = literal_eval(line)
          except:
            print('Cannot parse line', line)
            return False

          if not hasattr(o, 'num_seq'):
            o.num_seq = []
            o.output_order.append('num_seq')
          o.num_seq.append(line)
      return True
    
    obj = cls()

    text = text.strip()[1:-1].strip()

    items = []
    string_buff = []
    i = 0
    
    while i < len(text):
      symbol = text[i]

      if not (symbol == '{' and i < len(text) - 1 and text[i+1] == '\n'):
        string_buff.append(symbol)
        i+=1
      else:
        items.append(''.join(string_buff))
        string_buff = []

        node_text, _, end_idx = parse_parenthesis(text[i:])
        o = cls.parse_from_text(node_text)
        if not o: return None
        
        i = i + end_idx
        items.append(o)
    
    if string_buff:
      items.append(''.join(string_buff))

    last_item = None
    items_checked = 0
    if len(items) == 1:
      if not parse_text_into_object_attrs(obj, items[0].strip().split('\n')): return None
    else:
      for item in items:
        if isinstance(item, Node):
          if not last_item or not isinstance(last_item, str):
            print('Error: a child without header')
            return None
          
          lines = last_item.strip().split('\n')
          if not parse_text_into_object_attrs(obj, lines[:-1]): return None
          
          try:
            attr, val = lines[-1].split('=')
          except:
            print('Cannot parse header:', lines[-1])
            return None
          
          try: val = literal_eval(val)
          except: pass

          obj.output_order.append( ((attr, val), item) )
          items_checked += 2
        elif isinstance(item, str) and isinstance(last_item, str):
          print('Incorrect parsing')
          return None
        last_item = item
      if len(items) - items_checked > 1:
        print('Incorrect parsing')
        return None
      elif len(items) - items_checked == 1:
         lines = items[-1].strip().split('\n')
         if not parse_text_into_object_attrs(obj, lines): return None
    return obj

class Ship(Node):
  '''Wrapper for a Node object to work with ship configs'''
  def __init__(self):
    super().__init__()

  def get_stats(self):
    frame = self.find_by_attr('m_code', 47)[0]
    return frame

  def update_modules(self, parts, ol, vanilla_ol):
    children = self.find_by_attr('m_code', 15)
    '''Updates only mesh and scalar params for now'''

    #Stats which may differ between ship file and parts.seria
    #Parts only, ship only, unequal
    #parts: {'m_floor', 'm_stage', 'm_count'}
    #child: {'m_angle', 'm_sectors', 'm_scale.x', 'm_floor', 'm_mass', 'm_stage', 'm_owner_id'}
    #uneq: {'m_position.y', 'm_position.x', 'm_master_id', 'm_mass', 'm_id'}

    stats_to_ignore = set([ 'm_floor', 'm_stage', 'm_count', 'm_angle', 'm_sectors',
                           'm_owner_id', 'm_position.x', 'm_position.y', 'm_scale.x', 'm_scale.y',
                           'm_master_id', 'm_id',
                           'm_ed_rotate' #??????
                           ])

    #Make an exception for large fuel tanks
    
    for child in children:
      try:    part_entry = parts.get_by_oid(child.m_oid)[0]
      except: continue

      #Update mesh      
      child_mesh = child.get_children_by_name('m_mesh')[0]
      parts_mesh = part_entry.get_children_by_name('m_mesh')[0]

      child_mesh.m_size   = parts_mesh.m_size
      child_mesh.num_seq  = parts_mesh.num_seq[:]

      #Update mass
      child.m_mass = compute_part_mass(child)
      
      #Update non-child attrs
      for attr in part_entry.get_nonchildren_attrs():
        if attr not in stats_to_ignore:
          value = getattr(part_entry, attr)
          if isinstance(value, list): value = value[:]
          setattr(child, attr, value)
          if attr not in child.output_order:
            child.output_order.append
      
      #Update large tank explicitly
      if child.m_oid == 'MDL_FUEL_02': child.m_floor = part_entry.m_floor

      #Update radar range if this is a radar/elint
      if hasattr(child, 'm_name') and child.m_name == 'RADAR':
        try:
          vanilla_range = vanilla_ol.get_by_oid(child.m_oid)[0].m_mdl_radar
          new_range     = ol.get_by_oid(child.m_oid)[0].m_mdl_radar
        except:
          try:
            vanilla_range = vanilla_ol.get_by_oid(child.m_oid)[0].m_mdl_elint
            new_range     = ol.get_by_oid(child.m_oid)[0].m_mdl_elint
          except:
            #Some custom radar like the one on trade ships
            continue
        new_sectors = [ rng * 1.0 / vanilla_range * new_range for rng in child.m_sectors ]
        child.m_sectors = new_sectors

  def recompute_stats(self, ol, vanilla_ol, parts, verbose=False):
    self.update_modules(parts, ol, vanilla_ol)

    children  = self.find_by_attr('m_oid')
    
    #Global ship params which are a sum of individual module params
    sum_stats = { 
        'm_init_price'      : [ 'm_price', 'OL', 0, 0 ], #part stat, database file, def value, agg value
        'm_tele_price'      : [ 'm_price', 'OL', 0, 0 ], #part stat, database file, def value, agg value
        'm_tele_power_need' : [ 'm_mdl_power_need', 'OL', 0, 0],
        'm_tele_power_total'  : [ 'm_mdl_power', 'OL', 0, 0],
        'm_init_power' : [ 'm_mdl_power', 'OL', 0, 0],
        'm_tele_power_total_repaired' : [ 'm_mdl_power', 'OL', 0, 0],
        'm_tele_mass' : [ compute_part_mass, 'parts', 0, 0 ]
     }

    init_price  = 0
    tele_power_need = 0
    tele_power_total = 0
    tele_power_total_repaired = 0
    
    stat_object = self.get_stats()

    for child in children:
      oid  = child.m_oid
        
      try:
        stat = ol.get_by_oid(oid)[0]
      except:
        print('Cannot read an OL entry for', oid)
        stat = Node() #Can't do anything with it, so use an empty node which will return def value
      
      try:
        part = parts.get_by_oid(oid)[0]
      except:
        print(f'Cannot read a parts entry for {oid}, using the ship part value instead')
        part = child
      
      for key in sum_stats.keys():
        module_stat, where, def_value, agg_value = sum_stats[key]
        db = stat if where == 'OL' else part
        if isinstance(module_stat, str):
          new_stat = db.get(module_stat, def_value)
        else:
          new_stat = module_stat(db)
        agg_value += new_stat
        sum_stats[key][3] = agg_value
    
    for stat, values in sum_stats.items():
      new_value = values[3]
      old_value = getattr(stat_object, stat)
      if verbose and old_value != new_value: print(f'{stat}: {old_value} --> {new_value}')
      setattr(stat_object, stat, new_value)

    #TODO: UPDATE PARAMS WHICH DEPEND ON MASS
    #TODO: UPDATE HP PARAMS
    #Optional, since the game can do it itself

#It may be better to rewrite child classes as wrapper classes for Node
class OL(Node):
  '''A Node child class to work with OL.seria'''
  def __init__(self):
    super().__init__()

  def get_by_oid(self, oid):
    return self.find_by_attr('m_oid', oid)

class Parts(Node):
  '''A Node child class to work with parts.seria'''
  def __init__(self):
    super().__init__()

  def get_by_oid(self, oid):
    return self.find_by_attr('m_oid', oid)