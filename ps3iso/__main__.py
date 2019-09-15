__package__ = 'ps3iso'

import sys
import shutil
from argparse import ArgumentParser as _ArgumentParser
from pathlib import Path

from .game import Game


class ArgumentParserError(Exception):
    pass


class ArgumentParser(_ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(message, file=sys.stderr)
        raise ArgumentParserError()


def parse_args(argv=None):
    parser = ArgumentParser()
    parser.add_argument('-i', '--input',
                        type=Path,
                        required=True,
                        help='Path to the PS3 ISO file or directory containing PS3 ISO files')
    parser.add_argument('-f', '--format',
                        help='Format string to use for output or --rename target')
    parser.add_argument('--rename',
                        action='store_true',
                        help='Rename .iso and supporting files to a format string based on PS3 metadata')

    _args = parser.parse_args(argv)
    if _args.rename and _args.format is None:
        parser.error('-f/--format is required for rename operation')
    return _args


def main(argv=None):
    try:
        args = parse_args(argv)
    except ArgumentParserError:
        sys.exit(1)

    if shutil.which('isoinfo') is None:
        print("Error: 'isoinfo' is required, but could not be found in the system PATH.\n"
              'Please install it to continue:\n'
              '    Windows:  https://smithii.com/files/cdrtools-latest.zip\n'
              '    macOS:    brew install cdrtools\n'
              '    Linux:    apt/dnf install genisoimage\n')
        sys.exit(1)

    games = Game.search(args.input)

    if args.rename:
        if args.input.resolve().is_dir():
            print('Scanning directory for PS3 ISOs...')
        Game.rename_all(list(games), args.format)

    else:
        for game in games:
            game.print_info(args.format)


if __name__ == '__main__':
    main()
