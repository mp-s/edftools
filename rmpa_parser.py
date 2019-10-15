import struct

class RMPAParse:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read_header(self):
        # header_data = self._origin_data[0:0x30]
        self._filesize = len(self._origin_data)
        flag_route_header = self._get_4bytes_to_uint(0x08)
        flag_shape_header = self._get_4bytes_to_uint(0x10)
        flag_camera_header = self._get_4bytes_to_uint(0x18)
        flag_spawnpoint_header = self._get_4bytes_to_uint(0x20)

        position_route_header = self._get_4bytes_to_uint(0x24)
        position_shape_header = self._get_4bytes_to_uint(0x24)
        position_camera_header = self._get_4bytes_to_uint(0x24)
        position_spawnpoint_header = self._get_4bytes_to_uint(0x24)

    def _read_type_header(self, type_pos):
        type_head_size = 0x20
        bytes_ = self._get_content(type_pos, type_head_size)
        sub_header_num = self._get_4bytes_to_uint(0, bytes_)
        sub_header_block_start_position = self._get_4bytes_to_uint(0x4, bytes_)
        type_chunk_end_position = self._get_4bytes_to_uint(0x0C, bytes_)
        rmpa_identifier = self._get_4bytes_to_uint(0x10, bytes_)
        # name_str = self._get_string()

    def _read_sub_header(self, sub_header_pos):
        sub_header_size = 0x20
        bytes_ = self._get_content(sub_header_pos, sub_header_size)
        sub_chunk_end_position = self._get_4bytes_to_uint(0x08)
        name_str_length = self._get_4bytes_to_uint(0x10)
        name_str = self._get_string(0x14)
        base_data_num = self._get_4bytes_to_uint(0x18)
        base_data_block_start_position = self._get_4bytes_to_uint(0x1C)

    def _read_spawnpoint(self, spawnpoint_pos):
        sp_size = 0x40
        bytes_ = self._get_content(spawnpoint_pos, sp_size)
        unknown1 = self._get_4bytes_to_uint(0x04)
        rmpa_identifier = self._get_4bytes_to_uint(0x08)
        coord = [
            self._get_4bytes_to_float(0x0c),
            self._get_4bytes_to_float(0x10),
            self._get_4bytes_to_float(0x14)
        ]
        sec_coord = [
            self._get_4bytes_to_float(0x1c),
            self._get_4bytes_to_float(0x20),
            self._get_4bytes_to_float(0x24),
        ]
        name_str_length = self._get_4bytes_to_uint(0x30)
        name_str = self._get_4bytes_to_uint(0x34)

    def _get_4bytes_to_uint(self, offset:int, data_chunk:bytes = None) -> int:
        data = data_chunk if data_chunk else self._origin_data
        byte_ = data[offset:offset+4]
        int_ = int.from_bytes(byte_, byteorder=self._byteorder, signed=False)
        return int_

    def _get_4bytes_to_float(self, offset:int, data_chunk:bytes = None) -> float:
        data = data_chunk if data_chunk else self._origin_data
        byte_ = data[offset:offset+4]
        unpack_type = '>f' if self._byteorder == 'big' else '<f'
        float_ = struct.unpack(unpack_type, byte_)[0]
        return float_

    def _get_string(self, offset:int, index:int = 0) -> str:
        end_bytes = b'\x00\x00'
        str_buffer = []
        utf16_byte = b''

        while(end_bytes != utf16_byte):
            utf16_byte = self._origin_data[offset:offset+2]
            if end_bytes == utf16_byte:
                break
            str_buffer.append(utf16_byte)
            offset += 2
        bytes_ = b''.join(str_buffer)
        return bytes_.decode(encoding=self._encoding)


    def _get_content(self, offset1:int, offset2:int, data_chunk:bytes) -> bytes:
        _data = data_chunk[offset1:offset2]
        return _data

    def read(self, file_path):
        with open(file=file_path, mode='rb') as f:
            self._origin_data = f.read()
        _file_header = self._origin_data[0:4]
        valid_header = b'\x00PMR'   # Big Endian
        if valid_header == _file_header:
            self._byteorder = 'big'
            self._encoding = 'utf-16be'
        elif valid_header == _file_header[::-1]:
            self._byteorder = 'little'
            self._encoding = 'utf-16le'
        else:
            print('Error File Type!')
            input()
            return None

    def get_full_string(self):
        pass