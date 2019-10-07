import struct

from bvm_model import *
import float_hex

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
            result = [ptr2_chunk[i:i+4] for i in range(0, 16, 4)]
            jmp_index = int.from_bytes(result[0], byteorder=self._byteorder)
            str_ = self._get_string(result[1])
            self._asm_jmp_mark[jmp_index] = f'\n{str_} :'
            class_name_index = result[2].hex()
            global_var_count = int.from_bytes(result[3],byteorder=self._byteorder)
            if self._debug_mode:
                print(str_, f'block ptr:{jmp_index}, className_index:{class_name_index}, global stores count: {global_var_count}')
    
    def get_constructor(self):
        self._construct_lines = {}
        self.asm_decompiler(construct=True)
        pass

    '''
    函数名, 跳转点插入方案
    '''
    def asm_decompiler(self, construct = False):
        _construct_chunk = self._get_content(self._index_constructor, self._index_asm)
        self._asm_lines = {}
        _asm_chunk = self._get_content(self._index_asm, self._index_str)
        if construct:
            self._asm_decompiler(_construct_chunk, self._construct_lines)
            pass
        else:
            self._asm_decompiler(_asm_chunk, self._asm_lines)
            pass

    def _asm_decompiler(self, chunk:bytes, buffer_dict:dict) -> dict:
        # if construct:
        #     self.asm_chunk = self._get_content(self._index_constructor, self._index_asm)
        # else:
        # chunk = self._get_content(self._index_asm, self._index_str)
        offset = 0
        operands_use_int = ['cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 'cuscall3'] # unsigned int
        operands_use_offset = ['jmp', 'call', 'jmpf', 'jmpt', 'jmpe', 'jmpne']
        # self._asm_lines = {}
        # print_data = []

        while(offset < len(chunk)):
            opcode = chunk[offset:offset+1]
            _opcode_offset = offset
            offset += 1
            ukn_opcode = (f'-UNKNOWN-: {opcode.hex()}',0)
            opcode_asm, operand_len = asm_opcode.get(opcode, ukn_opcode)
            buffer = [opcode.hex(), opcode_asm] if self._debug_mode else [opcode_asm]

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

                if (4 == operand_len and opcode_asm != 'pushstr'):  # all floats
                    operand_str = self._convert_operand(operand, 4)  # float_hex.hex_to_float(operand)
                elif opcode_asm == 'push':  # all numbers
                    operand_str = self._convert_operand(operand, operand_len)
                elif opcode_asm == 'pushstr':   # all bytes offset
                    operand_str = self._get_string(operand, self._index_str)
                elif opcode_asm in operands_use_int:    # all int
                    operand_str = str(int.from_bytes(operand, byteorder=self._byteorder))
                elif opcode_asm in operands_use_offset:
                    pass
                    '''
                    获取jmp的操作数, (signed)
                    记录每句字节码当前位置,
                    jmp位置+操作数=要定位的字节码位置
                    字节码位置 添加 跳转标记
                    jmp替换位跳转标记
                    '''
                    operand_int = int(self._convert_operand(operand, operand_len))
                    mark_offset = _opcode_offset + operand_int
                    operand_str = f'location_{mark_offset}'
                    self._asm_jmp_mark[mark_offset] = f'\n{operand_str} :'
                else:
                    operand_str = operand.hex() if self._byteorder == 'big' else operand[::-1].hex()
                
                offset += operand_len
                buffer.append(operand_str)

            buffer_dict[_opcode_offset] = buffer
            # print_data.append('\t'.join(buffer))

        # return print_data
        return buffer_dict

    def output_data(self):
        out_buffer = []
        self.get_global_var_name()
        out_buffer.extend(self._global_vars)
        constructor_name = self._get_string(self._index_class.to_bytes(4, byteorder=self._byteorder))
        out_buffer.append(f'\n{constructor_name}::{constructor_name}:')
        for values in self._construct_lines.values():
            out_buffer.append('  '.join(values))
        for key, values in self._asm_lines.items():
            jump_mark_str = self._asm_jmp_mark.get(key, None)
            if jump_mark_str:
                out_buffer.append(jump_mark_str)
            if self._debug_mode:
                space_length = 16 - 4 - len(values[1])
                space_placeholder = ' ' * space_length
                if len(values) == 3:
                    out_buffer.append(f'{values[0]}  {values[1]}{space_placeholder}{values[2]}')
                else:
                    out_buffer.append('  '.join(values))
            else:
                space_length = 16 - 4 - len(values[0])
                space_placeholder = ' ' * space_length
                if len(values) == 2:
                    out_buffer.append(f'  {values[0]}{space_placeholder}{values[1]}')
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

    ''' 
    大/小端处理
    读取4字节的地址信息
    读取1/2/4的数据 (并转换)
    while方式读取string
    '''

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
        offset = int.from_bytes(offset, byteorder=self._byteorder)

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
        return int.from_bytes(self.data[offset:offset+4], byteorder=self._byteorder, signed=False) 

    def _get_content(self, offset1: int, offset2: int) -> bytes:
        data = self.data[offset1:offset2]
        return data

if __name__ == "__main__":
    import os, sys
    if len(sys.argv) == 1:
        path = r"d:\arena\EARTH DEFENSE FORCE 5\r\MISSION\M003\MISSION.BVM"
        file_path = path
        # print('Must import BVM file!')
        # sys.exit()
    else:
        file_path = sys.argv[1]
    if '.bvm' == os.path.splitext(file_path)[1].lower():
        print('oik')
        bvm_ = BvmData(file_path)
        bvm_.get_func_name()
        bvm_.get_constructor()
        bvm_.asm_decompiler()
        with open('r:/bvmoutput.asm', 'w') as f:
            f.write(bvm_.output_data())
