import argparse
import os
from utils.parsing import *
import shutil

parser = argparse.ArgumentParser(description='A ship .seria updater.')

parser.add_argument('--dir', type=str,
                    help='a directory with .seria files to update', default='../Objects/Designs')
parser.add_argument('--out', type=str,
                    help='a directory where to output updated files.', default='Ships_updated')
parser.add_argument('--OL', type=str,
                    help='path to the OL.seria', default='../Libraries/OL.seria')
parser.add_argument('--parts', type=str,
                    help='path to the parts.seria', default='../Libraries/parts.seria')
parser.add_argument('--vOL', type=str,
                    help='path to the vanilla .OL. "Vanilla" means the original OL used during the ship construction.', default='../Backups/Libraries/OL.seria')

                    
args = parser.parse_args()

def main(args):
    ol = OL.from_file(args.OL)
    vanilla_ol = OL.from_file(args.vOL)
    parts = Parts.from_file(args.parts)
    
    output_ships_path = args.out
    
    for ship in os.listdir(args.dir):
        if ship.endswith('.seria'):
            print(ship)
            out_path = os.path.join(output_ships_path, ship)
            ship_name = os.path.join(args.dir, ship)
            ship = Ship.from_file(ship_name)
            try:
                ship.recompute_stats(ol, vanilla_ol, parts, verbose=True)
                ship.write(out_path)
            except:
                try:
                    print('Cannot update global stats, recomputing local only')
                    ship = Ship.from_file(ship_name)
                    ship.update_modules(parts, ol, vanilla_ol)
                    ship.write(out_path)
                except:
                    print('Cannot update')
                    print('---------------------------')
            print()
        elif ship.endswith('.png'):
            dst = os.path.join(output_ships_path, ship)
            src = os.path.join(args.dir, ship)
            shutil.copyfile(src, dst)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)