
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
    b'\x6b': ('syscall', 1), b'\xab': ('syscall', 2),
    b'\x2c': ('syscall1', 0), b'\x6c': ('syscall1', 1), b'\xac': ('syscall1', 2), b'\xec': ('syscall1', 4),
    b'\x2d': ('syscall2', 0), b'\x6d': ('syscall2', 1), b'\xad': ('syscall2', 2),
    b'\x2e': ('syscall3', 0), b'\x6e': ('syscall3', 1),

    b'\x15': ('push', 0), b'\x33': ('push', 0), b'\x55': ('push', 1), b'\x95': ('push', 2), b'\xd5': ('push', 4),
    b'\x18': ('pushs', 0), b'\x58': ('pushs', 1), b'\x98': ('pushs', 2),

    b'\x1a': ('ldstr', 0), b'\x5a': ('ldstr', 1), b'\x9a': ('ldstr', 2),

    b'\x28': ('jmp', 0), b'\x68': ('jmp', 1), b'\xa8': ('jmp', 2),
    b'\x69': ('call', 1), b'\xa9': ('call', 2),

    b'\x30': ('exit', 0),

    b'\x16': ('store', 0), b'\x56': ('store', 1),
    b'\x19': ('stores', 0), b'\x59': ('stores', 1),
    b'\x14': ('load', 0), b'\x54': ('load', 1),
    b'\x17': ('loads', 0), b'\x57': ('loads', 1),

    b'\x1c': ('subs', 0), b'\x5c': ('subs', 1),
    b'\x5b': ('adds', 1), b'\x9b': ('adds', 2),

    b'\x35': ('beq', 0), b'\x75': ('beq', 1), b'\xb5': ('beq', 2),
    b'\x26': ('beqz', 0), b'\x66': ('beqz', 1), b'\xa6': ('beqz', 2),
    b'\x34': ('bne', 0), b'\x74': ('bne', 1), b'\xb4': ('bne', 2),
    b'\x27': ('bnez', 0), b'\x67': ('bnez', 1), b'\xa7': ('bnez', 2),

    b'\x2a': ('ret', 0), b'\x36': ('storePop', 0), b'\x02': ('pop', 0), b'\x03': ('dup', 0),

    b'\x09': ('neg', 1),  # 09 00
    b'\x1f': ('sez', 1),  # 1f 00
    b'\x0a': ('inc', 1),

    b'\x01': ('storePush', 1),
    b'\x04': ('add', 1),  # 04 00 word opcode
    b'\x20': ('slt', 1),
    b'\x23': ('sne', 1),
    b'\x1d': ('sand', 1),
    b'\x24': ('sge', 1),
}