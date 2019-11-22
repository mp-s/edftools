import argparse
import struct
from pathlib import Path

import bvm_model as mdl


class BvmData:

    def __init__(self, file_path: str, debug_flag: bool = False):
        self._debug_mode = debug_flag
        with open(file_path, 'rb') as f:
            self.data = f.read()
        if (self.data[0:4] == b'BVM '):
            self._byteorder = 'little'
            self._encoding = 'utf-16le'
        else:
            self._byteorder = 'big'
            self._encoding = 'utf-16be'
        self._read_header()
        self._global_vars = {}
        self._asm_jmp_mark = {}
        self._construct_lines = {}
        self._asm_lines = {}

    def _read_header(self):
        # self.size = self.get_offset(offset_list['data_align_index'])
        self._index_ptr_list = self._get_offset('pointer_list_index')
        self._count_ptr_list = self._get_offset('pointer_list_count')
        self._index_ptr2_list = self._get_offset('pointer_list2_index')
        self._count_ptr2_list = self._get_offset('pointer_list2_count')
        self._index_constructor = self._get_offset('store_chunk_index')
        self._index_asm = self._get_offset('asm_code_chunk_index')
        self._index_str = self._get_offset('string_chunk_index')
        self._index_class = self._get_offset('class_name_index')

    def get_global_var_name(self):
        size = self._count_ptr_list * 4
        offset2 = self._index_ptr_list + size
        ptr_data = self._get_content_with_ofs(self._index_ptr_list, offset2)
        assert len(ptr_data) == size
        ptr_list = [ptr_data[i:i+4] for i in range(0, size, 4)]
        for index, str_index in enumerate(ptr_list):
            str_ = self._get_string(str_index)
            self._global_vars[index] = str_

    def get_func_name(self):
        size = self._count_ptr2_list * 0x10
        ptr2_data = self._get_content_with_size(self._index_ptr2_list, size)
        assert len(ptr2_data) == size

        ptr2_list = [ptr2_data[i:i+0x10] for i in range(0, size, 0x10)]
        for ptr2_chunk in ptr2_list:
            _lst = [ptr2_chunk[i:i+4] for i in range(0, 0x10, 0x04)]
            jmp_mark_index, _fn_name_pos, arg_index, arg_count_store = _lst
            jmp_mark_index = self._get_int(jmp_mark_index)
            func_name = self._get_string(_fn_name_pos)
            # return uint
            arg_count = arg_count_store[0]
            # keep bytes type
            func_return_type_byte = arg_count_store[1:2]

            _index = self._get_int(arg_index)
            _arg_byte = self._get_content_with_size(_index, 1)
            if _arg_byte in mdl.func_arg_types:
                types_name = []
                if arg_count:
                    types = self._get_content_with_size(_index, arg_count)
                    for arg_type in types:
                        arg_type = arg_type.to_bytes(1, self._byteorder)
                        types_name.append(mdl.func_arg_types.get(arg_type))
                type_str = ', '.join(types_name)
                if func_return_type_byte != b'\x00':
                    return_type_str = mdl.func_arg_types.get(
                        func_return_type_byte)
                else:
                    return_type_str = ''
                return_string = f'\n{func_name}:   /- {return_type_str}({type_str})'
            else:
                class_name_ = self._get_string(arg_index)
                return_string = f'\n{class_name_}::{func_name}:'
            self._asm_jmp_mark[jmp_mark_index] = return_string
            if self._debug_mode:
                print(
                    func_name, f'block ptr:{jmp_mark_index}, className_index:{arg_index}, global stores count: {arg_count}')

    def get_constructor(self):
        _construct_chunk = self._get_content_with_ofs(
            self._index_constructor, self._index_asm)
        self.__asm_decompiler(_construct_chunk, self._construct_lines)
        pass

    def asm_decompiler(self):
        _asm_chunk = self._get_content_with_ofs(
            self._index_asm, self._index_str)
        self.__asm_decompiler(_asm_chunk, self._asm_lines)

    def __asm_decompiler(self, chunk: bytes, buffer_dict: dict) -> dict:
        offset = 0
        operands_use_uint = ['cuscall', 'cuscall0',
                             'cuscall1', 'cuscall2', 'cuscall3']
        operands_use_offset = ['jmp', 'call', 'jmpf', 'jmpt', 'jmpe', 'jmpne']

        while(offset < len(chunk)):
            opcode = chunk[offset:offset+1]
            _opcode_offset = offset
            offset += 1
            ukn_opcode = (f'-UNKNOWN-: {opcode.hex()}', 0)
            opcode_asm, operand_len = mdl.asm_opcode.get(opcode, ukn_opcode)
            buffer = [opcode.hex(), opcode_asm]

            if operand_len == 0:
                if opcode_asm == 'pushstr':    # "pushstr 0"
                    _ = self._get_string(bytes(0), self._index_str)
                    buffer.append(f'\"{_}\"')
                elif opcode == b'\x15' or 'cuscall' in opcode_asm:
                    buffer.append('0')
                elif opcode == b'\x33':
                    buffer.append('1')
                elif 'abs' in opcode_asm:   # "**abs 0"
                    buffer.append('0')
                    buffer.append(self._global_vars.get(0))
                elif 'rel' in opcode_asm:
                    buffer.append('0x00')
                else:
                    pass
            else:
                operand = chunk[offset:offset+operand_len]
                comments = None

                if (4 == operand_len and opcode_asm != 'pushstr'
                        and opcode_asm not in operands_use_uint
                        and opcode_asm not in operands_use_offset):  # all floats
                    operand_str = self._convert_operand(operand, 4)
                elif opcode_asm == 'push':  # all numbers
                    operand_str = self._convert_operand(operand, operand_len)
                elif opcode_asm == 'pushstr':   # all bytes offset
                    operand_str = f'\"{self._get_string(operand, self._index_str)}\"'
                elif opcode_asm in operands_use_uint:    # all int
                    operand_str = str(self._get_int(operand))
                    # 添加注释
                    if opcode_asm == 'cuscall0':
                        comments = mdl.call_func_types.get(operand_str, None)
                elif opcode_asm in operands_use_offset:
                    operand_int = int(
                        self._convert_operand2(operand, operand_len))
                    mark_offset = _opcode_offset + operand_int
                    operand_str = f'location_{mark_offset}'
                    self._asm_jmp_mark[mark_offset] = f'\n{operand_str} :'
                elif 'abs' in opcode_asm:
                    # 全局变量存放点
                    operand_int = self._get_int(operand)
                    operand_str = str(operand_int)
                    comments = self._global_vars.get(operand_int)
                else:
                    _ = operand.hex(
                    ) if self._byteorder == 'big' else operand[::-1].hex()
                    operand_str = f'0x{_}'
                    comments = mdl.get_asm_comment(opcode_asm, operand_str)

                offset += operand_len
                buffer.append(operand_str)
                if comments:
                    buffer.append(comments)

            buffer_dict[_opcode_offset] = buffer

        return buffer_dict

    def output_data(self) -> str:
        self.get_global_var_name()  # 全局变量名字
        self.get_func_name()        # 带名字函数
        self.get_constructor()      # 构造函数
        self.asm_decompiler()       # 字节码区反编译
        out_buffer = []
        # global vars
        for index, var_name in self._global_vars.items():
            out_buffer.append(f'name {var_name}    // {index}')
        constructor_name = self._get_string(
            self._index_class.to_bytes(4, byteorder=self._byteorder))
        out_buffer.append(f'\n{constructor_name}::{constructor_name}:')
        for values in self._construct_lines.values():
            if not self._debug_mode:
                values[0] = ''
            if len(values) == 3:
                out_buffer.append('  '.join(values))
            else:
                left_str = '  '.join(values[0:3])
                comment_str = '  '.join(values[3:])
                out_buffer.append(f'{left_str}    // {comment_str}')
        # assemble
        for key, values in self._asm_lines.items():
            jump_mark_str = self._asm_jmp_mark.get(key, None)
            if jump_mark_str:
                out_buffer.append(jump_mark_str)
            if not self._debug_mode:
                values[0] = ''
            space_length = 16 - 4 - len(values[1])
            space_placeholder = ' ' * space_length
            if len(values) == 3:
                out_buffer.append(
                    f'{values[0]}  {values[1]}{space_placeholder}{values[2]}')
            elif len(values) == 4:
                out_buffer.append(
                    f'{values[0]}  {values[1]}{space_placeholder}{values[2]}    // {values[3]}')
            elif len(values) > 4:
                comment_str = '  '.join(values[3:])
                out_buffer.append(
                    f'{values[0]}  {values[1]}{space_placeholder}{values[2]}    // {comment_str}')
            else:
                out_buffer.append('  '.join(values))

        return '\n'.join(out_buffer)

    def get_all_str(self):
        '''debug test'''
        index = self._get_offset('string_chunk_index')
        size = self._get_offset('class_name_index')
        end_bytes = b'\x00\x00'
        str_buffer = []
        str_list = []
        utf16_byte = b''
        offset = index
        while(offset < size):
            while(end_bytes != utf16_byte):
                utf16_byte = self.data[offset:offset+2]
                str_buffer.append(utf16_byte)
                offset += 2
            bytes_ = b''.join(str_buffer)
            str_ = bytes_.decode(encoding=self._encoding, errors='ignore')
            str_list.append(str_)
            str_buffer.clear()
            utf16_byte = b''
        return str_list

    def _convert_operand2(self, bytes_: bytes, bytes_length: int = 0) -> str:
        return int.from_bytes(bytes_, byteorder=self._byteorder, signed=True)

    def _convert_operand(self, bytes_: bytes, bytes_length: int) -> str:
        '''
        signed-int or float
        '''

        def get_unpack_type(length: int) -> str:
            if self._byteorder == 'little':
                p1 = '<'
            else:
                p1 = '>'
            p2 = {1: 'b',
                  2: 'h',
                  4: 'f'}
            return p1 + p2.get(length)
        unpack_type = get_unpack_type(bytes_length)
        str_ = str(struct.unpack(unpack_type, bytes_)[0])
        if bytes_length == 4:
            str_ = f'{str_}f'
        return str_

    def _get_string(self, offset: bytes, index: int = 0) -> str:
        end_bytes = b'\x00\x00'
        str_buffer = []
        utf16_byte = b''
        offset = self._get_int(offset) + index

        while(end_bytes != utf16_byte):
            utf16_byte = self.data[offset:offset+2]
            if end_bytes == utf16_byte:
                break
            str_buffer.append(utf16_byte)
            offset += 2

        bytes_ = b''.join(str_buffer)

        return bytes_.decode(encoding=self._encoding)

    def _get_offset(self, offset_name: str) -> int:
        offset = mdl.offset_list.get(offset_name)
        return self._get_int(self.data[offset:offset+4])

    def _get_content_with_ofs(self, offset1: int, offset2: int) -> bytes:
        data = self.data[offset1:offset2]
        return data

    def _get_content_with_size(self, offset: int, size: int = 0) -> bytes:
        data = self.data[offset:offset+size]
        return data

    def _get_int(self, byte_: bytes, signed_=False) -> int:
        return int.from_bytes(byte_, byteorder=self._byteorder, signed=signed_)


def run_main():
    args = parse_args()

    if args.source_path is None:
        str_ = input('drag file here and press Enter: ')
        source_path = Path(str_.strip('"'))
    else:
        source_path = Path(args.source_path)

    if args.destination_path:
        output_path = Path(args.destination_path)
    else:
        output_path = source_path.with_suffix('.asm')

    if '.bvm' == source_path.suffix.lower():
        print('working...')
        bvm_ = BvmData(source_path, debug_flag=args.debug)
        with output_path.open(mode='w', encoding='utf-8') as f:
            f.write(bvm_.output_data())
        print('done!')


def parse_args():
    description = 'bvm file decompiler'
    parse = argparse.ArgumentParser(description=description)

    help_ = 'input bvm file path'
    parse.add_argument('source_path', help=help_, nargs='?')
    help_ = 'output asm file path'
    parse.add_argument('destination_path', help=help_, nargs='?')

    help_ = 'enable debug mode'
    parse.add_argument('-d', '--debug', help=help_,
                       action='store_true', default=False)
    parse.add_argument('-t', action='store_true')

    return parse.parse_args()


if __name__ == "__main__":
    run_main()
