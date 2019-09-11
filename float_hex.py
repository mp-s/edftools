import struct
from enum import Enum

class Endian(Enum):
    LITTLE = 1
    BIG = 2

def hex_to_float(hexcode: bytes, endian: int = 1) -> str:
    if 1 == endian:
        type_endian = '<f'
    elif 2 == endian:
        type_endian = '>f'
        # return struct.unpack('>f', hexcode)[0]
    else:
        type_endian = '<f'
    return str(struct.unpack(type_endian, hexcode)[0])

def float_to_hex(float_num: float, endian: int = 1) -> str:
    if 1 == endian:
        return hex(struct.unpack('<I', struct.pack('<f', float_num))[0])
    elif 2 == endian:
        return hex(struct.unpack('<I', struct.pack('>f', float_num))[0])
    else:
        assert 'Wrong number'
        return None
