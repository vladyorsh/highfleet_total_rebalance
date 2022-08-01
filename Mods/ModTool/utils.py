from ast import literal_eval
import numpy as np
import copy

class Logger:
    def __init__(self):
        pass
    
    def log(self, * args, ** kwargs):
        print(*args, **kwargs)

class ShipEntry(object):
    def __init__(self, ship_names, difficulties=['easy', 'normal', 'hard'], spawn_chance=1.0):
        self.names = ship_names
        self.difficulties = difficulties
        self.spawn_chance = spawn_chance
            
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