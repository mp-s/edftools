import argparse
import sys
from pathlib import Path

from mission_util.bvm_compiler import BVMGenerate
from mission_util.bvm_decompiler import BvmData
from mission_util.rmpa_builder import RMPAGenerate
from mission_util.rmpa_parser import RMPAParse

BvmData.build_file = BvmData.output_file
RMPAGenerate.build_file = RMPAGenerate.generate_rmpa
RMPAParse.build_file = RMPAParse.generate_json


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("\nPress Enter key to exit.")
    sys.exit(-1)


sys.excepthook = show_exception_and_exit


def parse_args():
    description = 'bvm/rmpa/json/asm converter'
    parse = argparse.ArgumentParser(description=description)

    help_ = 'input file path'
    parse.add_argument('source_path', help=help_, nargs='?')
    help_ = 'output file path'
    parse.add_argument('destination_path', help=help_, nargs='?')

    help_ = 'enable debug mode'
    parse.add_argument('-d',
                       '--debug',
                       help=help_,
                       action='store_true',
                       default=False)
    # parse.add_argument('-t', action='store_true')

    return parse.parse_args()


def main():
    args = parse_args()

    if args.source_path is None:
        str_ = input('drag file here and press Enter: ')
        source_path = Path(str_.strip('"'))
    else:
        source_path = Path(args.source_path)

    dest_type_tbl = {
        '.bvm': '.asm',
        '.asm': '.bvm',
        '.rmpa': '.json',
        '.json': '.rmpa',
    }

    src_suffix = source_path.suffix.lower()

    if args.destination_path:
        output_path = Path(args.destination_path)
    else:
        output_path = source_path.with_suffix(dest_type_tbl.get(
            src_suffix, ''))

    src_type_tbl = {
        '.bvm': BvmData,
        '.asm': BVMGenerate,
        '.rmpa': RMPAParse,
        '.json': RMPAGenerate,
    }

    _obj_class = src_type_tbl.get(src_suffix)
    print('working...')
    obj = _obj_class(args.debug)
    obj.read(source_path)
    obj.build_file(output_path)
    print('done!')


if __name__ == "__main__":
    main()
