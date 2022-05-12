import argparse
import os
import copy
import importlib
import random
from utils.parsing import *

parser = argparse.ArgumentParser(description='A ship .seria updater.')

parser.add_argument('--save', type=str,
                    help='save file location to tweak.')
parser.add_argument('--output', type=str,
                    help='output path for a new save.', default='Saves_updated/profile.seria')
parser.add_argument('--config', type=str,
                    help='a .py file contatining SG configs', default='sg_config')
parser.add_argument('--vanilla', type=str,
                    help='Highfleet/Objects/Designs path', default='../Objects/Designs')
parser.add_argument('--custom', type=str,
                    help='Highfleet/Ships path', default='../Ships')
parser.add_argument('--verbose', action='store_true',
                    help='verbose output',  default=False)
                    

def sample_fleet_from_entries(sg_entry, difficulty):
    entries = [ random.choice(x.names) for x in sg_entry ] #Sample a random ship from several choices
    entries = [ ship for ship, entry in zip(entries, sg_entry) if (random.random() < entry.spawn_chance) and difficulty in entry.difficulties ] #Filter by difficulty/spawn rate
    return entries
    
                    
def main(args):
    config_path = args.config
    if config_path.endswith('.py'):
        config_path = config_path[:-3]
    
    if args.verbose: print('Loaded config')
    
    config = importlib.import_module(config_path)
    
    if args.verbose: print('Loading save...')
    
    save = Node.from_file(args.save)
    escadras = save.get_children_by_name('m_escadras')
    strike_groups = []
    carrier_groups= []
    
    ship_cache = {}
    
    for escadra in escadras: #Find SGs and carrier groups
        children = escadra.get_children_by_name('m_children')
        is_sg = False
        for child in children:
            if child.m_name in { 'Borey', 'Gryphon', 'Nomad', }:
                strike_groups.append(escadra)
                break
            elif child.m_name in { 'Longbow' }:
                carrier_groups.append(escadra)
                break
    
    if args.verbose:
        print('SGs:') #Print SGs
        for escadra in strike_groups:
            print(escadra.m_name)
            children = escadra.get_children_by_name('m_children')
            for child in children:
                print(child.m_name)
            print()
        print('-----------------------------------------------------------')
        print('AGs:') #Print carrier groups
        for escadra in carrier_groups:
            print(escadra.m_name)
            children = escadra.get_children_by_name('m_children')
            for child in children:
                print(child.m_name)
            print()
    
    difficulty_level = 'normal'
    if save.get('m_easymode', 'false') == 'true':
        difficulty_level = 'easy'
    elif save.get('m_hardmode', 'false') == 'true':
        difficulty_level = 'hard'
    if args.verbose: print('Detected difficulty level:', difficulty_level)
        
    for i, escadra in enumerate(strike_groups):        
        fleet_comp = config.STRIKE_GROUPS[i] if i in config.STRIKE_GROUPS.keys() else config.STRIKE_GROUPS['default']
        fleet_comp = sample_fleet_from_entries(fleet_comp, difficulty_level)
        
        if args.verbose: print(f'Escadra {escadra.m_name}, sampled new fleet composition: {fleet_comp}')
        
        ships = []
        for item in fleet_comp:
            ship = None
            if item in ship_cache.keys():
                ship = ship_cache[item]
            else:
                try:    ship = Ship.from_file(os.path.join(args.vanilla, item + '.seria'))
                except: ship = Ship.from_file(os.path.join(args.custom,  item + '.seria'))
                ship_cache[item] = ship
            ships.append(ship)
        
        replace_escadra_ships(escadra, ships)
    
    save.write(args.output)
    
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)