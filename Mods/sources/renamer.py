import argparse
import os
from utils.parsing import *

parser = argparse.ArgumentParser(description='A ship .seria updater.')

parser.add_argument('--dir', type=str,
                    help='directory to rename.')
parser.add_argument('--output', type=str,
                    help='output path for renamed ships.', default='Ships_renamed')
parser.add_argument('--paths', type=str, nargs='+',
                    help='ship paths to rename.')
                    
def main(args):
    paths = []
    if args.dir:
        paths = [ os.path.join(args.dir, item) for item in os.listdir(args.dir) if item.endswith('.seria') ]
    else:
        paths = args.paths
    
    for path in paths:
        ship = Ship.from_file(path)
        stat = ship.get_stats()
        
        print(f'Name: {ship.m_name}, enter new name without .seria:')
        new_name = input()
        
        ship.m_name = new_name
        stat.m_card_caption = stat.m_card_caption.replace(stat.m_ship_name, new_name)
        stat.m_ship_name = new_name
        
        #Clear the snapshot if it exists, remove if playing a version older than 1.151
        stat.remove('m_card_snapshot')
        
        output_path = os.path.join(args.output, new_name + '.seria')
        ship.write(output_path)
        
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)