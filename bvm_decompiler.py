import struct

import float_hex
from bvm_model import *


class BvmData:

    jmp_loc_count = 0
    # 添加debug参数, 减少不必要噪音
    def __init__(self, file_path: str, debug:int = False):
        self._debug_mode = debug
        with open(file_path, 'rb') as f:
            self.data = f.read()
        if (self.data[0:4] == b'BVM '):
            self._byteorder = 'little'
            self._encoding = 'utf-16le'
        else:
            self._byteorder = 'big'
            self._encoding = 'utf-16be'
        self._read_header()
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
        ptr_data = self._get_content(self._index_ptr_list, offset2)
        self._global_vars = []
        assert len(ptr_data) == size
        ptr_list = [ptr_data[i:i+4] for i in range(0, size, 4)]
        for index, str_index in enumerate(ptr_list):
            str_ = self._get_string(str_index)
            self._global_vars.append(f'name {str_} // {hex(index)[2:]}')
    
    def get_func_name(self):
        size = self._count_ptr2_list * 0x10
        end_offset = self._index_ptr2_list + size
        ptr2_data = self._get_content(self._index_ptr2_list, end_offset)
        assert len(ptr2_data) == size
        
        ptr2_list = [ptr2_data[i:i+0x10] for i in range(0, size, 16)]
        for ptr2_chunk in ptr2_list:
            _lst = [ptr2_chunk[i:i+4] for i in range(0, 16, 4)]
            jmp_mark_index = self._get_int(_lst[0])
            func_name = self._get_string(_lst[1])
            arg_index = _lst[2]
            arg_count = _lst[3][0]

            _index = self._get_int(arg_index)
            _arg_byte = self._get_content(_index, _index+1)
            if  _arg_byte in func_arg_types:
                types_name = []
                if arg_count:
                    types = self._get_content(_index, _index + arg_count)
                    for arg_type in types:
                        arg_type = arg_type.to_bytes(1, self._byteorder)
                        types_name.append(func_arg_types.get(arg_type))
                type_str = ', '.join(types_name)
                return_string = f'\n{func_name}:  // {func_name}({type_str})'
                pass # 有传参 有类型 后续处理
            else:
                class_name_ = self._get_string(arg_index)
                return_string = f'\n{class_name_}::{func_name}:'
            self._asm_jmp_mark[jmp_mark_index] = return_string
            if self._debug_mode:
                print(func_name, f'block ptr:{jmp_mark_index}, className_index:{arg_index}, global stores count: {arg_count}')
    
    def get_constructor(self):
        _construct_chunk = self._get_content(self._index_constructor, self._index_asm)
        self.__asm_decompiler(_construct_chunk, self._construct_lines)
        pass

    def asm_decompiler(self):
        _asm_chunk = self._get_content(self._index_asm, self._index_str)
        self.__asm_decompiler(_asm_chunk, self._asm_lines)


    def __asm_decompiler(self, chunk:bytes, buffer_dict:dict) -> dict:
        offset = 0
        operands_use_int = ['cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 'cuscall3'] # unsigned int
        operands_use_offset = ['jmp', 'call', 'jmpf', 'jmpt', 'jmpe', 'jmpne']
        # self._asm_lines = {}


        while(offset < len(chunk)):
            opcode = chunk[offset:offset+1]
            _opcode_offset = offset
            offset += 1
            ukn_opcode = (f'-UNKNOWN-: {opcode.hex()}',0)
            opcode_asm, operand_len = asm_opcode.get(opcode, ukn_opcode)
            buffer = [opcode.hex(), opcode_asm]

            # operand_len == 0
            if opcode_asm == 'pushstr' and operand_len == 0:    # "pushstr 0"
                buffer.append(self._get_string(self._index_str.to_bytes(4, byteorder=self._byteorder, signed=False)))
            elif opcode == b'\x15':
                buffer.append('0')
            elif opcode == b'\x33':
                buffer.append('1')
            else:
                pass

            if (operand_len):
                operand = chunk[offset:offset+operand_len]
                comments = None

                if (4 == operand_len and opcode_asm != 'pushstr'):  # all floats
                    operand_str = self._convert_operand(operand, 4)  # float_hex.hex_to_float(operand)
                elif opcode_asm == 'push':  # all numbers
                    operand_str = self._convert_operand(operand, operand_len)
                elif opcode_asm == 'pushstr':   # all bytes offset
                    operand_str = self._get_string(operand, self._index_str)
                elif opcode_asm in operands_use_int:    # all int
                    operand_str = str(self._get_int(operand))
                    # 添加注释
                    comments = call_func_types.get(operand_str, None)
                elif opcode_asm in operands_use_offset:
                    operand_int = int(self._convert_operand(operand, operand_len))
                    mark_offset = _opcode_offset + operand_int
                    operand_str = f'location_{mark_offset}'
                    self._asm_jmp_mark[mark_offset] = f'\n{operand_str} :'
                else:
                    operand_str = operand.hex() if self._byteorder == 'big' else operand[::-1].hex()
                
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
        out_buffer.extend(self._global_vars)
        # constor
        constructor_name = self._get_string(self._index_class.to_bytes(4, byteorder=self._byteorder))
        out_buffer.append(f'\n{constructor_name}::{constructor_name}:')
        for values in self._construct_lines.values():
            out_buffer.append('  '.join(values))
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
                out_buffer.append(f'{values[0]}  {values[1]}{space_placeholder}{values[2]}')
            elif len(values) > 3:
                comment_str = '  '.join(values[2:])
                out_buffer.append(f'{values[0]}  {values[1]}{space_placeholder}{values[2]} // {comment_str}')
            else:
                out_buffer.append('  '.join(values))


        return '\n'.join(out_buffer)

    def get_all_str(self):
        index = self.get_offset('string_chunk_index')
        size = self.get_offset('class_name_index')
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

    def _convert_operand(self, bytes_:bytes, bytes_length:int) -> str:
        '''
        signed int or
        float
        '''
        enum_length = {
            1: '<b',
            2: '<h',
            4: '<f',
        } if self._byteorder == 'little' else {
            1: '>b',
            2: '>h',
            4: '>f',
        }
        return str(struct.unpack(enum_length.get(bytes_length), bytes_)[0])

    def _get_string(self, offset: bytes, index: int = 0) -> str:
        end_bytes = b'\x00\x00'
        str_buffer = []
        utf16_byte = b''
        offset = self._get_int(offset)

        if index:
            _data = self.data[index:]
        else:
            _data = self.data

        while(end_bytes != utf16_byte):
            utf16_byte = _data[offset:offset+2]
            if end_bytes == utf16_byte:
                break
            str_buffer.append(utf16_byte)
            offset += 2

        bytes_ = b''.join(str_buffer)

        return bytes_.decode(encoding=self._encoding)

    def _get_offset(self, offset_name: str) -> int:
        offset = offset_list.get(offset_name)
        return self._get_int(self.data[offset:offset+4]) 

    def _get_content(self, offset1: int, offset2: int) -> bytes:
        data = self.data[offset1:offset2]
        return data

    def _get_int(self, byte_:bytes, signed_=False) -> int:
        return int.from_bytes(byte_, byteorder=self._byteorder, signed=signed_)

if __name__ == "__main__":
    import os, sys
    if len(sys.argv) == 1:
        # path = r"d:\arena\EARTH DEFENSE FORCE 5\r\MISSION\M003\MISSION.BVM"
        # file_path = path
        print('BVM file required!')
        sys.exit()
    else:
        file_path = sys.argv[1]
    _sp = os.path.splitext(file_path)
    if len(sys.argv) == 3:
        output_path = sys.argv[2]
    else:
        output_path = f'{_sp[0]}.asm'
    if '.bvm' == _sp[1].lower():
        print('working...')
        bvm_ = BvmData(file_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bvm_.output_data())
        print('done!')