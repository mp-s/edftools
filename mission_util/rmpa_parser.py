#! python3
import base64
import json
import struct
from pathlib import Path

from . import util
from .rmpa_config import *


class RMPAParse:
    def __init__(self, debug_flag: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug_flag = debug_flag

    def _read_type_header(self, self_pos, type_name):
        ''' read type header and get type block content '''
        type_head_size = 0x20
        bytes_ = self._get_content_bytes(self_pos, size=type_head_size)

        def byte_uint(pos: int) -> int:
            return util.uint_from_4bytes(util.get_4bytes(bytes_, pos),
                                         self._byteorder)

        sub_header_num = byte_uint(0x00)
        sub_header_block_start_pos = byte_uint(0x04)
        type_chunk_end_position = byte_uint(0x0C)
        # rmpa_identifier = self._get_4bytes_to_uint(0x10, bytes_)
        name_bytes_pos = byte_uint(0x18)
        name_str = self._get_string(name_bytes_pos, index=self_pos)
        # read sub headers
        _unamed_list = []
        for _ in range(sub_header_num):
            sub_size = 0x20
            sub_current_pos = _ * sub_size + sub_header_block_start_pos + self_pos
            _unamed_list.append(
                self._read_sub_header(sub_current_pos, type_name))
            pass
        type_header_dict = {
            RmpaConfig.type_group_name: name_str,
            RmpaConfig.sub_enum_groups: _unamed_list,
        }
        if self._debug_flag:
            type_header_dict[RmpaConfig.type_chunk_end_position] = hex(
                type_chunk_end_position)
            type_header_dict[RmpaConfig.sub_header_count] = sub_header_num
            type_header_dict[RmpaConfig.current_block_position] = hex(self_pos)
        return type_header_dict

    def _read_sub_header(self, sub_header_pos, type_name):
        ''' read sub-enum header and get base data block content '''
        sub_header_size = 0x20
        self_pos = sub_header_pos
        bytes_ = self._get_content_bytes(sub_header_pos, size=sub_header_size)

        def byte_uint(pos: int) -> int:
            return util.uint_from_4bytes(util.get_4bytes(bytes_, pos),
                                         self._byteorder)

        base_type_dict = {
            RmpaConfig.type_spawnpoint: self._read_spawnpoint,
            RmpaConfig.type_route: self._read_waypoint,
            RmpaConfig.type_shape: self._read_shape,
        }

        # sub_chunk_end_position = self._get_4bytes_to_uint(0x08, bytes_)
        # name_str_length = self._get_4bytes_to_uint(0x10, bytes_)
        name_bytes_pos = byte_uint(0x14)
        name_str = self._get_string(name_bytes_pos, index=self_pos)
        base_data_num = byte_uint(0x18)
        base_data_block_start_pos = byte_uint(0x1C)
        _base_list = []
        _base_data_size = {
            RmpaConfig.type_route: 0x3c,
            RmpaConfig.type_shape: 0x30,
            # 'camera':,
            RmpaConfig.type_spawnpoint: 0x40,
        }
        for idx in range(base_data_num):
            data_size = _base_data_size.get(type_name)
            base_data_current_pos = idx * data_size + base_data_block_start_pos + self_pos
            # get type function
            _fn = base_type_dict.get(type_name, str)
            _base_list.append(_fn(base_data_current_pos))
        ld = {
            RmpaConfig.sub_enum_name: name_str,
            RmpaConfig.base_data_list: _base_list,
        }
        if self._debug_flag:
            ld[RmpaConfig.base_data_count] = base_data_num
            ld[RmpaConfig.current_block_position] = hex(self_pos)
        return ld

    def _read_spawnpoint(self, spawnpoint_def_pos):
        ''' get spawnpoint blocks and parse to dict. '''
        sp_size = 0x40
        self_pos = spawnpoint_def_pos
        bytes_ = self._get_content_bytes(spawnpoint_def_pos, size=sp_size)
        sp = TypeSpawnPoint(self._byteorder)
        sp.from_bytes_block(bytes_)
        sp.name = self._get_string(sp.name_in_rmpa_pos, self_pos)
        _ld = sp.to_dict(self._debug_flag)
        if self._debug_flag:
            _ld[RmpaConfig.current_block_position] = hex(self_pos)
        return _ld

    def _read_waypoint(self, route_def_pos):
        ''' get waypoint blocks and parse to dict. '''
        wp_size = 0x3C
        self_pos = route_def_pos
        bytes_ = self._get_content_bytes(route_def_pos, size=wp_size)

        wp = TypeWayPoint(self._byteorder)
        wp.from_bytes_block(bytes_)
        wp.name = self._get_string(wp.name_in_rmpa_pos, self_pos)

        _next_wp_start_pos = wp.next_wp_list_blk_in_rmpa_start_pos
        # _next_wp_end_pos = waypoint.next_wp_list_blk_in_rmpa_end_pos
        _next_wpblk_abs_start_pos = self_pos + _next_wp_start_pos
        _next_wp_blk_size = wp.next_wp_count * 0x04
        next_wp_blk_bytes = self._get_content_bytes(_next_wpblk_abs_start_pos,
                                                    _next_wp_blk_size)

        extra_sgo_abs_pos = self_pos + wp.extra_sgo_in_rmpa_start_pos
        _extra_sgo_bytes = self._get_content_bytes(extra_sgo_abs_pos,
                                                   wp.extra_sgo_size)

        wp.from_bytes_block_extra(next_wp_blk_bytes, _extra_sgo_bytes)
        _ddd = wp.to_dict(self._debug_flag)
        if self._debug_flag:
            _ddd[RmpaConfig.current_block_position] = hex(self_pos)
            _ddd[RmpaConfig.route_next_block_pos] = hex(
                _next_wpblk_abs_start_pos)
            _ddd[RmpaConfig.route_sgo_block_pos] = hex(extra_sgo_abs_pos)
        return _ddd

    def _read_shape(self, shape_pos):
        ''' get shape blocks and parse to dict. '''
        shape_set_size = 0x30
        self_pos = shape_pos
        bytes_ = self._get_content_bytes(self_pos, size=shape_set_size)
        shape = TypeShape(self._byteorder)
        shape.from_bytes_block(bytes_)
        shape.name = self._get_string(shape.name_in_rmpa_pos, self_pos)
        shape.shape_type = self._get_string(shape.shape_type_in_rmpa_pos,
                                            self_pos)
        shape_data_block_abs_pos = self_pos + shape.size_data_in_rmpa_pos
        size_bytes = self._get_content_bytes(shape_data_block_abs_pos, 0x40)
        shape.from_bytes_block_size_data(size_bytes)
        _ldd = shape.to_dict(self._debug_flag)
        if self._debug_flag:
            _ldd[RmpaConfig.current_block_position] = hex(self_pos)
            _ldd[RmpaConfig.shape_size_pos] = hex(shape_data_block_abs_pos)
        return _ldd

    def _read_struct(self):
        ''' parse rmpa file '''
        header_data = self._origin_data[0:0x30]
        h = RmpaHeader(self._byteorder)
        h.parse_block(header_data)
        _head_dict = h.generate_dict()
        self._struct = {}
        for type_name, type_data in _head_dict.items():
            type_head_pos, flag = type_data
            if flag:
                self._struct[type_name] = self._read_type_header(
                    type_head_pos, type_name)

    def _get_4bytes_to_uint(self,
                            offset: int,
                            data_chunk: bytes = None) -> int:
        data = data_chunk if data_chunk else self._origin_data
        byte_ = data[offset:offset + 4]
        int_ = int.from_bytes(byte_, byteorder=self._byteorder, signed=False)
        return int_

    def _get_string(self, offset: int, index: int = 0) -> str:
        end_bytes = b'\x00\x00'
        str_buffer = []
        utf16_byte = b''
        offset = offset + index
        while (end_bytes != utf16_byte):
            utf16_byte = self._origin_data[offset:offset + 2]
            if end_bytes == utf16_byte:
                break
            str_buffer.append(utf16_byte)
            offset += 2
        bytes_ = b''.join(str_buffer)
        return bytes_.decode(encoding=self._encoding)

    def _get_content_bytes(self, offset1: int, size: int = 0) -> bytes:
        _data = self._origin_data
        if size:
            _data_r = _data[offset1:offset1 + size]
        else:
            _data_r = bytes()
        return _data_r

    def read(self, file_path):
        ''' read file to buffer '''
        with open(file=file_path, mode='rb') as f:
            self._origin_data = f.read()
        _file_header = self._origin_data[0:4]
        valid_header = b'\x00PMR'  # Big Endian
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

    def output_file(self, output_path: Path):
        self._read_struct()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mmJSONEncoder().encode(self._struct))
            # json.dump(self._struct, f,cls=mmJSONEncoder)  # using cls.iterencode()

    def get_all_string(self):
        '''debug test
        '''
        position_spawnpoint_header = self._get_4bytes_to_uint(0x24)
        _type_bytes = self._get_content_bytes(position_spawnpoint_header,
                                              size=0x20)
        index = self._get_4bytes_to_uint(0x18, _type_bytes)
        size = len(self._origin_data)
        end_bytes = b'\x00\x00'
        str_buffer = []
        try:
            isinstance(self._original_str_list, list)
        except (AttributeError, NameError):
            self._original_str_list = []
        else:
            return self._original_str_list
        utf16_byte = b''
        offset = index + position_spawnpoint_header
        while (offset < size):
            while (end_bytes != utf16_byte):
                utf16_byte = self._origin_data[offset:offset + 2]
                str_buffer.append(utf16_byte)
                offset += 2
            bytes_ = b''.join(str_buffer)
            str_ = bytes_.decode(encoding=self._encoding, errors='ignore')
            self._original_str_list.append(str_)
            str_buffer.clear()
            utf16_byte = b''
        return self._original_str_list


class RmpaHeader:
    ''' parse rmpa file header '''
    def __init__(self, byteorder: str):
        super().__init__()
        self._byteorder = byteorder

    def parse_block(self, block_data: bytes):
        def get_uint(pos: int) -> int:
            return util.uint_from_4bytes(util.get_4bytes(block_data, pos),
                                         self._byteorder)

        self.flag_route = get_uint(0x08)
        self.flag_shape = get_uint(0x10)
        self.flag_camera = get_uint(0x18)
        self.flag_spawnpoint = get_uint(0x20)
        self.pos_route = get_uint(0x0c)
        self.pos_shape = get_uint(0x14)
        self.pos_camera = get_uint(0x1c)
        self.pos_spawnpoint = get_uint(0x24)

    def generate_dict(self):
        return {
            RmpaConfig.type_route: (self.pos_route, self.flag_route),
            RmpaConfig.type_shape: (self.pos_shape, self.flag_shape),
            RmpaConfig.type_camera: (self.pos_camera, self.flag_camera),
            RmpaConfig.type_spawnpoint:
            (self.pos_spawnpoint, self.flag_spawnpoint),
        }


class mmJSONEncoder(json.JSONEncoder):
    ''' custom JSON indent '''
    def __init__(self, *args, **kwargs):
        self.ensure_ascii = False
        self.indent = 2
        super().__init__(ensure_ascii=self.ensure_ascii,
                         indent=self.indent,
                         *args,
                         **kwargs)
        self.current_indent = 0
        self.current_indent_str = ""

    def encode(self, o):
        # Special Processing for lists
        if isinstance(o, (list, tuple)):
            primitives_only = True
            for item in o:
                if isinstance(item, (list, tuple, dict)):
                    primitives_only = False
                    break
            output = []
            if primitives_only:
                for item in o:
                    output.append(json.dumps(item))
                return "[ " + ", ".join(output) + " ]"
            else:
                self.current_indent += self.indent
                self.current_indent_str = " " * self.current_indent
                for item in o:
                    output.append(self.current_indent_str + self.encode(item))
                self.current_indent -= self.indent
                self.current_indent_str = " " * self.current_indent
                return "[\n" + ",\n".join(
                    output) + "\n" + self.current_indent_str + "]"
        elif isinstance(o, dict):
            output = []
            self.current_indent += self.indent
            self.current_indent_str = " " * self.current_indent
            for key, value in o.items():
                output.append(self.current_indent_str + json.dumps(key) +
                              ": " + self.encode(value))
            self.current_indent -= self.indent
            self.current_indent_str = " " * self.current_indent
            return "{\n" + ",\n".join(
                output) + "\n" + self.current_indent_str + "}"
        else:
            return json.dumps(o, ensure_ascii=self.ensure_ascii)



if __name__ == "__main__":
    from time import sleep
    print('none')
    sleep(4)
