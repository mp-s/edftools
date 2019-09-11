

offset_list = {
    'pointer_list_count': 0x18,
    'pointer_list_index': 0x1c,
    'pointer_list2_count': 0x20,
    'pointer_list2_index': 0x24,
    'store_chunk_index': 0x30,
    'asm_code_chunk_index': 0x34,
    'string_chunk_index': 0x38,
    'class_name_index': 0x3c,
    'data_size_offset_index': 0x44,
    'data_align_index': 0x4c
}

class bvm_data:
    asm_opcode = {
        b'\x6b':1, b'\xab':2,
        b'\x2c':0, b'\x6c':1, b'\xac':2, b'\xec':4,
        b'\x2d':0, b'\x6d':1, b'\xad':2,
        b'\x2e':0, b'\x6e':1,
        b'\x15':0, b'\x33':0, b'\x55':1, b'\x95':2, b'\xd5':4,
        b'\x18':0, b'\x58':1, b'\x98':2,
        b'\x1a':0, b'\x5a':1, b'\x9a':2,
        b'\x28':0, b'\x68':1, b'\xa8':2,
        b'\x69':1, b'\xa9':2,
        b'\x30':0,
        b'\x16':0, b'\x56':1,
        b'\x19':0, b'\x59':1,
        b'\x14':0, b'\x54':1,
        b'\x17':0, b'\x57':1,
        b'\x1c':0, b'\x5c':1,
        b'\x04':1, b'\x09':1, b'\x1f':1,
        b'\x5b':1, b'\x9b':2,
        b'\x2a':0,
        b'\x66':1,
        b'\x34':0, b'\x74':1, b'\xb4':2,
    }
    def __init__(self, file_path: str):
        read_size = 4
        with open(file_path, 'rb') as f:
            self.data = f.read()
        self.read_header()

    def read_header(self):
        # self.size = self.get_offset(offset_list['data_align_index'])
        self.index_ptr_list = self.get_offset(offset_list.get('pointer_list_index'))
        self.count_ptr_list = self.get_offset(offset_list.get('pointer_list_count'))
        self.index_ptr2_list = self.get_offset(offset_list.get('pointer_list2_index'))
        self.count_ptr2_list = self.get_offset(offset_list.get('pointer_list2_count'))
        self.index_asm = self.get_offset(offset_list.get('asm_code_chunk_index'))
        self.index_str = self.get_offset(offset_list.get('string_chunk_index'))
        self.index_class = self.get_offset(offset_list.get('class_name_index'))
    
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
        print_data = []
        while(offset < len(self.asm_chunk)):
            opcode = self.asm_chunk[offset:offset+1]
            offset += 1
            operand_len = self.asm_opcode.get(opcode, 0)
            buffer = [opcode.hex()]
            if(operand_len):
                operand = self.asm_chunk[offset:offset+operand_len]
                buffer.append(operand.hex())
                offset += operand_len
            print_data.append(str(buffer))
            # print('いる？', self.asm_opcode.get(opcode, b'no------'))
        return print_data
    
    def get_all_str(self):
        index = self.get_offset(offset_list.get('string_chunk_index'))
        size = self.get_offset(offset_list.get('class_name_index'))
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
            print(str_)
            str_buffer.clear()
#             print(offset)
            utf16_byte = b''
        
    
    def get_string(self, offset: bytes):
        end_bytes = b'\x00\x00'
        buffer = []
        utf16_byte = b''
        offset = int.from_bytes(offset, byteorder='little')
        while(end_bytes != utf16_byte):
            utf16_byte = self.data[offset:offset+2]
            buffer.append(utf16_byte)
            offset += 2
        bytes_ = b''.join(buffer)
        return bytes_.decode(encoding='utf-16le')
        
            
    def get_offset(self, offset1: int) -> int:
        return int.from_bytes(self.data[offset1:offset1+4], byteorder='little') 

    def get_content(self, offset1: int, offset2: int) -> bytes:
        data = self.data[offset1:offset2]
        return data