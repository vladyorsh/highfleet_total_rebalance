import argparse
import os
import copy
import importlib
import random
from utils.parsing import *

parser = argparse.ArgumentParser(description='A SG save editor.')

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
    
def update_escadra(args, escadra, index, difficulty_level, ship_cache, config):
    fleet_comp = config.STRIKE_GROUPS[index]
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
    
    
def main(args):
    config_path = args.config
    if config_path.endswith('.py'):
        config_path = config_path[:-3]
    
    config = importlib.import_module(config_path)
    if args.verbose: print('Loaded config')
    if args.verbose: print('Loading save...')
    
    save = Node.from_file(args.save)
    escadras = save.get_children_by_name('m_escadras')
    strike_groups = []
    carrier_groups= []
    launcher_groups= []
    
    ship_cache = {}
    
    for escadra in escadras: #Find SGs and carrier groups
        children = escadra.get_children_by_name('m_children')
        is_sg = False
        names = { child.m_name for child in children }
        
        if names & { 'Borey', 'Gryphon', 'Nomad', }:
            if 'Typhon' in names: launcher_groups.append(escadra)
            else: strike_groups.append(escadra)
        
        elif 'Longbow' in names:
            carrier_groups.append(escadra)
    
    if args.verbose:
        print('SGs:') #Print SGs
        for escadra in strike_groups:
            print(escadra.m_name)
            children = escadra.get_children_by_name('m_children')
            for child in children:
                print(child.m_name)
            print()
        print('-----------------------------------------------------------')
        print('Launcher groups:')
        for escadra in launcher_groups:
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
    
    #Check the difficulty level and the game phase (endgame or not)
    difficulty_level = 'normal'
    if save.get('m_easymode', 'false') == 'true':
        difficulty_level = 'easy'
    elif save.get('m_hardmode', 'false') == 'true':
        difficulty_level = 'hard'
    
    endgame = None
    for obj in save.output_order:
        if type(obj) == str and'KHIVA_LANDING' in obj:
            endgame = trigger[-1] == '0'
            break
    
    if args.verbose:
        print('Detected difficulty level:', difficulty_level)
        print('Endgame phase:', endgame)
    
    #Update existing groups based on the difficulty level and the game phase
    for i, escadra in enumerate(strike_groups):
        index = i if not endgame else 6
        index = 'endgame' if endgame and (6 not in config.STRIKE_GROUPS.keys()) else index
        index = index if index in config.STRIKE_GROUPS.keys() else 'default'
        
        update_escadra(args, escadra, index, difficulty_level, ship_cache, config)
    
    for i, escadra in enumerate(launcher_groups):
        index = 'launcher'
        update_escadra(args, escadra, index, difficulty_level, ship_cache, config)
    
    save.write(args.output)
    
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)