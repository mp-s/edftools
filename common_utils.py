import struct


def int_from_4bytes(bytes_: bytes, byteorder: str) -> int:
    return int.from_bytes(bytes_, byteorder=byteorder)


def int_from_4bytes_little(bytes_: bytes) -> int:
    return int.from_bytes(bytes_, byteorder='little')


def int_from_4bytes_big(bytes_: bytes) -> int:
    return int.from_bytes(bytes_, byteorder='big')


def uint_from_4bytes(bytes_: bytes, byteorder: str) -> int:
    return int.from_bytes(bytes_, byteorder=byteorder, signed=True)


def uint_from_4bytes_little(bytes_: bytes) -> int:
    return int.from_bytes(bytes_, byteorder='little', signed=True)


def uint_from_4bytes_big(bytes_: bytes) -> int:
    return int.from_bytes(bytes_, byteorder='big', signed=True)


def float_from_4bytes(bytes_: bytes, byteorder: str) -> float:
    if byteorder == 'little':
        fmt = '<f'
    elif byteorder == 'big':
        fmt = '>f'
    else:
        return 0.0
    return struct.unpack(fmt, bytes_)[0]


def int_to_4bytes(number: int, byteorder: str) -> bytes:
    return number.to_bytes(4, byteorder=byteorder)


def float_to_4bytes(number: float, byteorder: str) -> bytes:
    if byteorder == 'little':
        fmt = '<f'
    elif byteorder == 'big':
        fmt = '>f'
    return struct.pack(fmt, number)


def split_content_with_size(content: bytes, start: int, size: int = 0) -> bytes:
    if size == 0:
        return bytes()
    return content[start:start+size]


def get_4bytes(content: bytes, pos: int) -> bytes:
    return content[pos:pos+4]


def get_string(origin_data: bytes,
               offset: int,
               index: int = 0,
               encoding: str = 'utf-16le') -> str:
    end_bytes = b'\x00\x00'
    str_buffer = []
    utf16_byte = b''
    offset = offset + index
    while(end_bytes != utf16_byte):
        utf16_byte = origin_data[offset:offset+2]
        if end_bytes == utf16_byte:
            break
        str_buffer.append(utf16_byte)
        offset += 2
    bytes_ = b''.join(str_buffer)
    return bytes_.decode(encoding=encoding)
