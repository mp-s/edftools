import struct

import bvm_model
import float_hex

class bvm_data:

    jmp_loc_count = 0
    unpack_lengh = {
        1:'<b',
        2:'<h',
    }

    def __init__(self, file_path: str):
        with open(file_path, 'rb') as f:
            self.data = f.read()
        self.read_header()

    def read_header(self):
        # self.size = self.get_offset(offset_list['data_align_index'])
        self.index_ptr_list = self.get_offset('pointer_list_index')
        self.count_ptr_list = self.get_offset('pointer_list_count')
        self.index_ptr2_list = self.get_offset('pointer_list2_index')
        self.count_ptr2_list = self.get_offset('pointer_list2_count')
        self.index_asm = self.get_offset('asm_code_chunk_index')
        self.index_str = self.get_offset('string_chunk_index')
        self.index_class = self.get_offset('class_name_index')
    
    def slice_ptr1(self):
        size = self.count_ptr_list * 4
        offset2 = self.index_ptr_list + size
        ptr_data = self.get_content(self.index_ptr_list, offset2)
        assert len(ptr_data) == size
        ptr_list = [ptr_data[i:i+4] for i in range(0, size, 4)]
        for str_index in ptr_list:
            str_ = self.get_string(str_index)
            print(str_)
    
    def slice_ptr2(self):
        size = self.count_ptr2_list * 16
        offset2 = self.index_ptr2_list + size
        ptr2_data = self.get_content(self.index_ptr2_list, offset2)
        assert len(ptr2_data) == size
        ptr2_list = [ptr2_data[i:i+16] for i in range(0, size, 16)]
        for ptr2_chunk in ptr2_list:
            result = tuple(ptr2_chunk[i:i+4] for i in range(0, 16, 4))
            str_ = self.get_string(result[1])
            print(str_, 'block ptr:', result)
    
    def asm_decompiler(self):
        self.asm_chunk = self.get_content(self.index_asm, self.index_str)
        offset = 0
        line_num = 0
        line_index_dict = {}
        int_operands = ['cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 'cuscall3']
        print_data = []
        while(offset < len(self.asm_chunk)):
            opcode = self.asm_chunk[offset:offset+1]
            opcode_offset = str(offset)
            line_index_dict[opcode_offset] = line_num
            offset += 1
            ukn_opcode = (f'-UNKNOWN-: {opcode.hex()}',0)
            opcode_asm, operand_len = bvm_model.asm_opcode.get(opcode, ukn_opcode)
            buffer = [str(line_num), opcode_offset, opcode.hex(), opcode_asm]
            if opcode_asm == 'pushstr' and operand_len == 0:    # "pushstr 0"
                buffer.append(self.get_string(struct.pack('<I',self.index_str)))
            elif opcode == b'\x15':
                buffer.append('0')
            elif opcode == b'\x33':
                buffer.append('1')
            else:
                pass
            if (operand_len):
                operand = self.asm_chunk[offset:offset+operand_len]
                if (4 == operand_len and opcode_asm != 'pushstr'):
                    operand_str = float_hex.hex_to_float(operand)
                elif opcode_asm == 'push':
                    operand_str = str(struct.unpack(self.unpack_lengh.get(operand_len, '<i'), operand)[0])
                elif opcode_asm == 'pushstr':
                    operand_str = self.get_string(operand, self.index_str)
                elif opcode_asm in int_operands:
                    operand_str = str(int.from_bytes(operand, byteorder='little'))
                # elif 'jmp' in opcode_asm:
                #     operand_address = struct.unpack(self.unpack_lengh.get(operand_len, '<i'), operand)[0]
                #     next_jmp_address = offset + operand_address
                #     jmp_line = line_index_dict.get(next_jmp_address, offset)
                #     jmp_str = f'location_{self.jmp_loc_count}:'
                #     self.jmp_loc_count += 1
                #     print_data.insert(jmp_line, jmp_str)
                else:
                    operand_str = operand.hex()
                offset += operand_len
                buffer.append(operand_str)
            print_data.append('\t'.join(buffer))
            line_num += 1
        return print_data

    def get_jmp_name(self):
        _str = f'jmp_loc_{self.jmp_loc_count}'
        self.jmp_loc_count += 1
        return _str

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
            str_ = bytes_.decode(encoding='utf-16le', errors='ignore')
            str_list.append(str_)
            str_buffer.clear()
            utf16_byte = b''
        return str_list

    def get_string(self, offset: bytes, index: int = 0) -> str:
        end_bytes = b'\x00\x00'
        buffer = []
        utf16_byte = b''
        offset = int.from_bytes(offset, byteorder='little')
        if index:
            _data = self.data[index:]
        else:
            _data = self.data
        while(end_bytes != utf16_byte):
            utf16_byte = _data[offset:offset+2]
            buffer.append(utf16_byte)
            offset += 2
        bytes_ = b''.join(buffer)
        return bytes_.decode(encoding='utf-16le')

    def get_offset(self, offset_name: str) -> int:
        offset = bvm_model.offset_list.get(offset_name)
        return int.from_bytes(self.data[offset:offset+bvm_model.read_size], byteorder='little') 

    def get_content(self, offset1: int, offset2: int) -> bytes:
        data = self.data[offset1:offset2]
        return data

