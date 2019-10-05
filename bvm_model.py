
read_size = 4

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

asm_opcode = {
    b'\x01': ('cvtstore', 1),
    b'\x02': ('pop', 0),
    b'\x03': ('pushtop', 0),

    b'\x04': ('add', 1),  # 04 00 word opcode
    b'\x05': ('sub', 1),
    b'\x06': ('mult', 1),
    b'\x07': ('div', 1),
    b'\x08': ('mod', 1),
    b'\x09': ('neg', 1),  # 09 00
    b'\x0a': ('inc', 1),
    b'\x0b': ('dec', 1),

    # 新加
    b'\x0c': ('sar', 0),
    b'\x0d': ('sll', 0),
    b'\x0e': ('and', 0),
    b'\x0f': ('or', 0),
    b'\x10': ('xor', 0),
    b'\x11': ('not', 0),
    b'\x12': ('ftoi', 0),
    b'\x13': ('itof', 0),

    b'\x14': ('loadabs', 0), b'\x54': ('loadabs', 1),
    # next at 33
    b'\x15': ('push', 0), b'\x55': ('push', 1), b'\x95': ('push', 2), b'\xd5': ('push', 4),
    b'\x16': ('storeabs', 0), b'\x56': ('storeabs', 1),
    b'\x17': ('loadrel', 0), b'\x57': ('loadrel', 1),
    b'\x18': ('pushrel', 0), b'\x58': ('pushrel', 1), b'\x98': ('pushrel', 2),
    b'\x19': ('storerel', 0), b'\x59': ('storerel', 1),

    b'\x1a': ('pushstr', 0), b'\x5a': ('pushstr', 1), b'\x9a': ('pushstr', 2),
    b'\x1b': ('addrel', 0), b'\x5b': ('addrel', 1), b'\x9b': ('addrel', 2),
    b'\x1c': ('subrel', 0), b'\x5c': ('subrel', 1),

    b'\x1d': ('test2z', 1),
    b'\x1e': ('test2nz', 1),
    b'\x1f': ('testz', 1),  # 1f 00
    b'\x20': ('testg', 1),
    b'\x21': ('testge', 1),
    b'\x22': ('teste', 1),
    b'\x23': ('testne', 1),
    b'\x24': ('testle', 1),
    b'\x25': ('testl', 1),
    b'\x26': ('jmpf', 0), b'\x66': ('jmpf', 1), b'\xa6': ('jmpf', 2), b'\xe6': ('jmpf', 4),
    b'\x27': ('jmpt', 0), b'\x67': ('jmpt', 1), b'\xa7': ('jmpt', 2),
    b'\x28': ('jmp', 0), b'\x68': ('jmp', 1), b'\xa8': ('jmp', 2),
    b'\x29': ('call', 0), b'\x69': ('call', 1), b'\xa9': ('call', 2), b'\xe9': ('call', 4),
    b'\x2a': ('ret', 0),

    b'\x2b': ('cuscall', 0), b'\x6b': ('cuscall', 1), b'\xab': ('cuscall', 2),
    b'\x2c': ('cuscall0', 0), b'\x6c': ('cuscall0', 1), b'\xac': ('cuscall0', 2), b'\xec': ('syscall1', 4),
    b'\x2d': ('cuscall1', 0), b'\x6d': ('cuscall1', 1), b'\xad': ('cuscall1', 2),
    b'\x2e': ('cuscall2', 0), b'\x6e': ('cuscall2', 1),
    b'\x2f': ('cuscall3', 0), b'\x6f': ('cuscall3', 1),

    b'\x30': ('exit', 0),

    # unused in retail
    b'\x31': ('printnum', 1),
    b'\x32': ('printstr', 0),

    b'\x33': ('push', 0), # push 1, before with 15
    b'\x34': ('jmpne', 0), b'\x74': ('jmpne', 1), b'\xb4': ('jmpne', 2),
    b'\x35': ('jmpe', 0), b'\x75': ('jmpe', 1), b'\xb5': ('jmpe', 2),

    b'\x36': ('store', 0),

}