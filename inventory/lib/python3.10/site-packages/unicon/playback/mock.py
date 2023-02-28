
import argparse
from ._mock import create_yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--recorded-data', help='Recorded data')
    parser.add_argument('--output', help='File to save yaml')
    parser.add_argument('--hostname', help='Device hostname (default: Router)',
                        type=str, default='switch')
    parser.add_argument('--allow-repeated-commands',
                        help='Allow saving the output of repeated commands',
                        action='store_true')
    parser.add_argument('--os',
                        help='Device os',
                        default=None)
    args = parser.parse_args()

    create_yaml(args.recorded_data, args.hostname, args.output,
                allow_repeated_commands=args.allow_repeated_commands,
                os=args.os)
