import float_hex
import struct

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
        b'\x6b':('syscall',1), b'\xab':('syscall',2),
        b'\x2c':('syscall1',0), b'\x6c':('syscall1',1), b'\xac':('syscall1',2), b'\xec':('syscall1',4),
        b'\x2d':('syscall2',0), b'\x6d':('syscall2',1), b'\xad':('syscall2',2),
        b'\x2e':('syscall3',0), b'\x6e':('syscall3',1),

        b'\x15':('push',0), b'\x33':('push',0), b'\x55':('push',1), b'\x95':('push',2), b'\xd5':('push',4),
        b'\x18':('pushs',0), b'\x58':('pushs',1), b'\x98':('pushs',2),
        
        b'\x1a':('ldstr',0), b'\x5a':('ldstr',1), b'\x9a':('ldstr',2),
        
        b'\x28':('jmp',0), b'\x68':('jmp',1), b'\xa8':('jmp',2),
        b'\x69':('call',1), b'\xa9':('call',2),

        b'\x30':('exit',0),

        b'\x16':('store',0), b'\x56':('store',1),
        b'\x19':('stores',0), b'\x59':('stores',1),
        b'\x14':('load',0), b'\x54':('load',1),
        b'\x17':('loads',0), b'\x57':('loads',1),

        b'\x1c':('subs',0), b'\x5c':('subs',1),
        b'\x5b':('adds',1), b'\x9b':('adds',2),

        b'\x35':('beq',0), b'\x75':('beq',1), b'\xb5':('beq',2), 
        b'\x26':('beqz',0), b'\x66':('beqz',1),b'\xa6':('beqz',2),
        b'\x34':('bne',0), b'\x74':('bne',1),b'\xb4':('bne',2),
        b'\x27':('bnez',0), b'\x67':('bnez',1),b'\xa7':('bnez',2),

        b'\x2a':('ret',0),b'\x36':('storePop',0),b'\x02':('pop',0),b'\x03':('dup',0),

        b'\x09':('neg',1), # 09 00
        b'\x1f':('sez',1), # 1f 00
        b'\x0a':('inc',1), 
        
        b'\x01':('storePush', 1),
        b'\x04':('add',1), # 04 00 word opcode
        b'\x20':('slt',1),
        b'\x23':('sne',1),
        b'\x1d':('sand',1),
        b'\x24':('sge',1),
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
            opcode_asm, operand_len = self.asm_opcode.get(opcode, (f'-UNKNOWN-: {opcode.hex()}',0))
            buffer = [opcode_asm]
            if opcode_asm == 'ldstr' and operand_len == 0:
                buffer.append(self.get_string(struct.pack('<I',self.index_str)))
            if (operand_len):
                operand = self.asm_chunk[offset:offset+operand_len]
                if (4 == operand_len and opcode_asm != 'ldstr'):
                    operand_str = float_hex.hex_to_float(operand)
                elif opcode_asm == 'ldstr':
                    operand_str = self.get_string(operand, self.index_str)
                else:
                    operand_str = operand.hex()
                offset += operand_len
                buffer.append(operand_str)
            print_data.append('\t'.join(buffer))
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
            # print(offset)
            utf16_byte = b''
        
    
    def get_string(self, offset: bytes, index: int = 0):
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
        

    def get_offset(self, offset1: int) -> int:
        return int.from_bytes(self.data[offset1:offset1+4], byteorder='little') 

    def get_content(self, offset1: int, offset2: int) -> bytes:
        data = self.data[offset1:offset2]
        return data

