import argparse
import os
import sys
from pathlib import Path

import common_utils as util

string_list = []
name_num_lst = []


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("\nPress Enter key to exit.")
    sys.exit(-1)


sys.excepthook = show_exception_and_exit


class AWEParse:
    def __init__(self):
        super().__init__()
        self.list_length = None
        self.name_table = {}

    def read(self, path_str: str):
        with open(path_str, 'rb') as f:
            # read header
            header_bytes = f.read(4)
            verified_header = b'AWBE'
            if header_bytes == verified_header:
                self._byteorder = 'little'
            elif header_bytes == verified_header[::-1]:
                self._byteorder = 'big'
            else:
                print('file type error')
                raise FileNotFoundError

            # awe content
            if self._byteorder:
                f.seek(0x08)
                self.list_length = util.uint_from_4bytes(
                    f.read(4), self._byteorder)
                f.seek(0)
                self.bytes_data = f.read()

    def _uifb(self, position: int) -> int:
        return util.uint_from_4bytes(self.bytes_data[position:position + 4],
                                     self._byteorder)

    def parse(self):
        # 输入 awe 读取文件数
        str_ptr_lst_start = 0x0c
        file_num_lst_start = 0x10

        str_ptr_list_head_pos = self._uifb(str_ptr_lst_start)
        file_num_list_head_pos = self._uifb(file_num_lst_start)

        # get {serial: fileName, ...}
        for index in range(self.list_length):
            str_ptr_self_pos = index * 0x04 + str_ptr_list_head_pos
            str_ofs = self._uifb(str_ptr_self_pos)
            str_pos = str_ofs + str_ptr_self_pos
            file_name = get_string(self.bytes_data, str_pos)

            num_pos = index * 0x02 + file_num_list_head_pos
            file_num_b = self.bytes_data[num_pos:num_pos + 2]
            file_num = int.from_bytes(file_num_b, byteorder=self._byteorder)
            self.name_table[file_num] = file_name


class AWBParse(util.LargeFileObject):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.list_length = None
        # self.file_path = file_path
        self.file_content_table = {}

    def check(self):
        # check file header
        header_bytes = self.file_mmap[0:4]
        verified_header = b'AFS2'
        if header_bytes == verified_header:
            self._byteorder = 'little'
        elif header_bytes == verified_header[::-1]:
            self._byteorder = 'big'
        else:
            print('file type error')
            raise FileNotFoundError

        files_num_pos = 0x08
        self.list_length = self._uint_from_position(files_num_pos)

    def _uint_from_position(self, position: int) -> int:
        _b = self.file_mmap[position:position + 4]
        return util.uint_from_4bytes(_b, self._byteorder)

    def parse(self):
        self.check()
        flags_pos = 0x04
        defined_padding_pos = 0x0c
        file_num_blk_head_pos = 0x10

        defined_padding = self._uint_from_position(defined_padding_pos)
        file_content_blk_head_pos = file_num_blk_head_pos + self.list_length * 0x02
        if self._uint_from_position(flags_pos) & 0x200:
            _pos_bytes_len = 0x02
        else:
            _pos_bytes_len = 0x04
        for index in range(self.list_length):
            file_num_pos = index * 0x02 + file_num_blk_head_pos
            file_num = int.from_bytes(
                self.file_mmap[file_num_pos:file_num_pos + 2],
                byteorder=self._byteorder)
            content_start_pos = index * _pos_bytes_len + file_content_blk_head_pos
            content_end_pos = content_start_pos + _pos_bytes_len
            content_start_pos = self._uint_from_position(content_start_pos)
            content_start_pos = padding_size(content_start_pos,
                                             defined_padding)
            content_end_pos = self._uint_from_position(content_end_pos)
            self.file_content_table[file_num] = [
                content_start_pos, content_end_pos
            ]
            pass
        pass


# 输入 awe 读取文件数
# 查找对应 awb 无则要求外部输入
# 检查 awb 文件数是否与 awe 读取的一致
# 开始操作
# 获得文件编号
# 获得文件名
# 获得文件内容偏移
# 批量写入文件
def extract(awe_path: str, awb_path: str, extract_path: str = None):
    awe_path = Path(awe_path)
    awb_path = Path(awb_path)
    if not awe_path.exists() or not awb_path.exists():
        raise FileNotFoundError

    if extract_path is not None:
        output_dir = Path(extract_path)
    else:
        output_dir = Path(awe_path.with_suffix('.output'))

    if output_dir.is_file():
        raise FileExistsError
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    awe = AWEParse()
    awe.read(awe_path)
    with AWBParse(awb_path) as awb:
        awb.check()
        if awe.list_length != awb.list_length:
            print('awe or awb file wrong')
            raise FileNotFoundError
        awe.parse()
        awb.parse()

        progress_count = 0
        print('total: ', awe.list_length)

        for serial, file_name in awe.name_table.items():
            output_path = output_dir / f'{file_name}.hca'
            start_pos, end_pos = awb.file_content_table.get(serial)

            if progress_count % (awe.list_length // 10) == 0:
                print(progress_count, '...')
            progress_count += 1

            with open(output_path, 'wb') as f_hca:
                f_hca.write(awb.file_mmap[start_pos:end_pos])


def padding_size(original_size: int, padding: int) -> int:
    _integer = original_size // padding
    if _integer == original_size / padding:
        return original_size
    else:
        return (_integer + 1) * padding


def get_string(data: bytes, offset: int) -> str:
    end_bytes = b'\x00'
    str_buffer = []
    name_byte = b''

    while (end_bytes != name_byte):
        name_byte = data[offset:offset + 1]
        if end_bytes == name_byte:
            break
        str_buffer.append(name_byte)
        offset += 1

    bytes_ = b''.join(str_buffer)
    return bytes_.decode(encoding='ascii')


def parse_args():
    description = "edf's awe AND awb extractor"
    parse = argparse.ArgumentParser(description=description)

    help_awe = 'awe file path'
    parse.add_argument('awe_path', help=help_awe, nargs='?')
    help_awb = 'awb file path'
    parse.add_argument('awb_path', help=help_awb, nargs='?')
    help_out = 'output path (optional)'
    parse.add_argument('output_path', help=help_out, nargs='?')

    parse.add_argument('--awe', help=help_awe)
    parse.add_argument('--awb', help=help_awb)
    parse.add_argument('-o', '--output', help=help_out)

    return parse.parse_args()


def main():
    args = parse_args()

    if args.awe_path is None and args.awe is None:
        _awe_path = input('drag AWE file here and press Enter :  ')
        _awe_path = Path(_awe_path.strip('"'))
    elif args.awe_path:
        _awe_path = Path(args.awe_path)
    elif args.awe:
        _awe_path = Path(args.awe)

    if args.awb_path is None and args.awb is None:
        _awb_path = input('drag AWB file here and press Enter :  ')
        _awb_path = Path(_awb_path.strip('"'))
    elif args.awb_path:
        _awb_path = Path(args.awb_path)
    elif args.awb:
        _awb_path = Path(args.awb)

    if args.output_path is None and args.output is None:
        _output_dir = input(
            '\n----!Optional----\n drag output directory here and Press Enter, \n or just Press Enter.\n'
        )
        _output_dir = _output_dir.strip('"')
    elif args.output_path:
        _output_dir = Path(args.output_path)
    elif args.output:
        _output_dir = Path(args.output)
    else:
        _output_dir = None

    if _output_dir:
        _output_dir = Path(_output_dir)
    else:
        _output_dir = None

    print('-' * 20)

    extract(_awe_path, _awb_path, _output_dir)


if __name__ == "__main__":
    main()
