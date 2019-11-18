import struct
import base64
import rmpa_config as cfg

class RMPAParse:

    def __init__(self, debug_flag = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug_flag = debug_flag

    def _read_header(self):
        # header_data = self._origin_data[0:0x30]
        self._filesize = len(self._origin_data)
        flag_route_header = self._get_4bytes_to_uint(0x08)
        flag_shape_header = self._get_4bytes_to_uint(0x10)
        flag_camera_header = self._get_4bytes_to_uint(0x18)
        flag_spawnpoint_header = self._get_4bytes_to_uint(0x20)

        position_route_header = self._get_4bytes_to_uint(0x0C)
        position_shape_header = self._get_4bytes_to_uint(0x14)
        position_camera_header = self._get_4bytes_to_uint(0x1C)
        position_spawnpoint_header = self._get_4bytes_to_uint(0x24)
        self._head_dict = {
            cfg.type_route: (position_route_header, flag_route_header),
            cfg.type_shape: (position_shape_header, flag_shape_header),
            cfg.type_camera: (position_camera_header, flag_camera_header),
            cfg.type_spawnpoint: (position_spawnpoint_header, flag_spawnpoint_header),
        }


    def _read_type_header(self, type_pos, type_name):
        type_head_size = 0x20
        self_pos = type_pos
        bytes_ = self._get_content_bytes(type_pos, size=type_head_size)

        sub_header_num = self._get_4bytes_to_uint(0x00, bytes_)
        sub_header_block_start_pos = self._get_4bytes_to_uint(0x04, bytes_)
        type_chunk_end_position = self._get_4bytes_to_uint(0x0C, bytes_)
        # rmpa_identifier = self._get_4bytes_to_uint(0x10, bytes_)
        name_bytes_pos = self._get_4bytes_to_uint(0x18, bytes_)
        name_str = self._get_string(name_bytes_pos, index=self_pos)
        # read sub headers
        _unamed_list = []
        for _ in range(sub_header_num):
            sub_size = 0x20
            sub_current_pos = _ * sub_size + sub_header_block_start_pos + self_pos
            _unamed_list.append(self._read_sub_header(sub_current_pos, type_name))
            pass
        type_header_dict = {
            cfg.type_group_name: name_str,
            cfg.sub_enum_groups: _unamed_list,
        }
        if self._debug_flag:
            type_header_dict[cfg.type_chunk_end_position] = type_chunk_end_position
            type_header_dict[cfg.sub_header_count] = sub_header_num
            type_header_dict[cfg.current_block_position] = self_pos
        return type_header_dict

    def _read_sub_header(self, sub_header_pos, type_name):
        sub_header_size = 0x20
        self_pos = sub_header_pos
        bytes_ = self._get_content_bytes(sub_header_pos, size=sub_header_size)
        base_type_dict = {
            cfg.type_spawnpoint: self._read_spawnpoint,
            cfg.type_route: self._read_routes,
            cfg.type_shape: self._read_shape_set,
        }

        # sub_chunk_end_position = self._get_4bytes_to_uint(0x08, bytes_)
        # name_str_length = self._get_4bytes_to_uint(0x10, bytes_)
        name_bytes_pos = self._get_4bytes_to_uint(0x14, bytes_)
        name_str = self._get_string(name_bytes_pos, index=self_pos)
        base_data_num = self._get_4bytes_to_uint(0x18, bytes_)
        base_data_block_start_pos = self._get_4bytes_to_uint(0x1C, bytes_)
        _base_list = []
        _base_data_size = {
            cfg.type_route: 0x3c,
            cfg.type_shape: 0x30,
            # 'camera':,
            cfg.type_spawnpoint: 0x40,
        }
        for _ in range(base_data_num):
            data_size = _base_data_size.get(type_name)
            base_data_current_pos = _ * data_size + base_data_block_start_pos + self_pos
            _fn = base_type_dict.get(type_name, str)
            _base_list.append(_fn(base_data_current_pos))
        ld = {
            cfg.sub_enum_name: name_str,
            cfg.base_data_list: _base_list,
        }
        if self._debug_flag:
            ld[cfg.base_data_count] = base_data_num
            ld[cfg.current_block_position] = hex(self_pos)
        return ld

    def _read_spawnpoint(self, spawnpoint_def_pos):
        sp_size = 0x40
        self_pos = spawnpoint_def_pos
        bytes_ = self._get_content_bytes(spawnpoint_def_pos, size=sp_size)

        # sub_group_end_pos = self._get_4bytes_to_uint(0x04, data_chunk=bytes_)
        # rmpa_identifier = self._get_4bytes_to_uint(0x08, data_chunk=bytes_)
        coord = [
            self._get_4bytes_to_float(x, data_chunk=bytes_)
            for x in range(0x0c, 0x18, 4)
        ]
        sec_coord = [
            self._get_4bytes_to_float(x, data_chunk=bytes_)
            for x in range(0x1c, 0x28, 4)
        ]
        # name_str_length = self._get_4bytes_to_uint(0x30, data_chunk=bytes_)
        name_str_pos = self._get_4bytes_to_uint(0x34, data_chunk=bytes_)
        name_str = self._get_string(name_str_pos, self_pos)

        _ld = {
            cfg.base_name: name_str,
            cfg.spawnpoint_pos_1: coord,
            cfg.spawnpoint_pos_2: sec_coord,
        }
        if self._debug_flag:
            _ld[cfg.current_block_position] = hex(self_pos)
        return _ld

    def _read_routes(self, route_def_pos):
        rt_size = 0x3C
        self_pos = route_def_pos
        bytes_ = self._get_content_bytes(route_def_pos, size=rt_size)
        current_route_number = self._get_4bytes_to_uint(0x00, bytes_)
        next_route_count = self._get_4bytes_to_uint(0x04, bytes_)
        next_route_bind_block_start_pos = self._get_4bytes_to_uint(0x08, bytes_)
        # next_route_bind_block_end_pos = self._get_4bytes_to_uint(0x10, bytes_)
        route_bind_pos = self_pos + next_route_bind_block_start_pos
        rout_p_size = next_route_count * 0x04
        route_bind_bytes = self._get_content_bytes(route_bind_pos, size=rout_p_size)
        route_p = [
            self._get_4bytes_to_uint(x, route_bind_bytes)
            for x in range(0, rout_p_size, 4)
        ]

        # rmpa_identifier = self._get_4bytes_to_uint(0x14, bytes_)

        extra_sgo_size = self._get_4bytes_to_uint(0x18, bytes_)
        extra_sgo_pos = self._get_4bytes_to_uint(0x1c, bytes_)
        if extra_sgo_size:
            extra_sgo_bytes = self._get_content_bytes(
                extra_sgo_pos + self_pos, size=extra_sgo_size)
            extra_sgo_endian = extra_sgo_bytes[0:4]
            up_code = '<f' if extra_sgo_endian == b'SGO\x00' else '>f'
            extra_sgo_b64 = struct.unpack(up_code, extra_sgo_bytes[0x28:0x2c])[0]
        else:
            extra_sgo_b64 = 'False'
        # name_str_length = self._get_4bytes_to_uint(0x20, bytes_)
        name_bytes_pos = self._get_4bytes_to_uint(0x24, bytes_)
        name_str = self._get_string(name_bytes_pos, self_pos) if name_bytes_pos else ''
        coord = [ 
            self._get_4bytes_to_float(x, bytes_)
            for x in range(0x28, 0x34, 4) 
        ]

        _ddd = {
            cfg.route_number: current_route_number,
            cfg.base_name: name_str,
            cfg.route_position: coord,
            cfg.waypoint_width: extra_sgo_b64,
            cfg.route_next_block: route_p,
        }
        if self._debug_flag:
            _ddd[cfg.current_block_position] = hex(self_pos)
            _ddd[cfg.route_next_block_pos] = hex(route_bind_pos)
            _ddd[cfg.route_sgo_block_pos] = hex(extra_sgo_pos + self_pos)
        return _ddd

    def _read_shape_set(self, shape_pos):
        shape_set_size = 0x30
        self_pos = shape_pos
        bytes_ = self._get_content_bytes(self_pos, size=shape_set_size)

        # shape_type_name_length = self._get_4bytes_to_uint(0x04, bytes_)
        shape_type_name_pos = self._get_4bytes_to_uint(0x08, bytes_)
        shape_type_name_str = self._get_string(shape_type_name_pos, self_pos)
        # shape_var_name_length = self._get_4bytes_to_uint(0x0c, bytes_)
        shape_var_name_pos = self._get_4bytes_to_uint(0x10, bytes_)
        shape_var_name_str = self._get_string(shape_var_name_pos, self_pos)
        shape_data_pos = self._get_4bytes_to_uint(0x24, bytes_)
        shape_data_abs_pos = shape_data_pos + self_pos
        shape_data_list = self._read_shape_data(shape_data_abs_pos)
        _ldd = {
            cfg.shape_type_name: shape_type_name_str,
            cfg.shape_variable_name: shape_var_name_str,
            cfg.shape_position_data: shape_data_list,
        }
        if self._debug_flag:
            _ldd[cfg.current_block_position] = hex(shape_data_abs_pos)
            _ldd[cfg.shape_size_pos] = shape_data_abs_pos
        return _ldd

    def _read_shape_data(self, shape_pos):
        shape_data_size = 0x40
        bytes_ = self._get_content_bytes(shape_pos, size=shape_data_size)

        pos_x = self._get_4bytes_to_float(0x00, bytes_)
        pos_y = self._get_4bytes_to_float(0x04, bytes_)
        pos_z = self._get_4bytes_to_float(0x08, bytes_)
        rectangle_x = self._get_4bytes_to_float(0x10, bytes_)
        rectangle_y = self._get_4bytes_to_float(0x14, bytes_)
        rectangle_z = self._get_4bytes_to_float(0x18, bytes_)

        sphere_diameter = self._get_4bytes_to_float(0x20, bytes_)
        retangele_extra = self._get_4bytes_to_float(0x24, bytes_)
        
        cylinder_diameter = self._get_4bytes_to_float(0x30, bytes_)
        cylinder_height = self._get_4bytes_to_float(0x34, bytes_)
        _lst = [
            pos_x, pos_y, pos_z,
            rectangle_x, rectangle_y, rectangle_z,
            sphere_diameter, retangele_extra,
            cylinder_diameter, cylinder_height,
        ]
        return _lst

    def _read_struct(self):
        self._read_header()
        self._struct = {}
        for type_name, type_data in self._head_dict.items():
            type_head_pos, flag = type_data
            if flag:
                self._struct[type_name] = self._read_type_header(type_head_pos, type_name)

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
        offset = offset + index
        while(end_bytes != utf16_byte):
            utf16_byte = self._origin_data[offset:offset+2]
            if end_bytes == utf16_byte:
                break
            str_buffer.append(utf16_byte)
            offset += 2
        bytes_ = b''.join(str_buffer)
        return bytes_.decode(encoding=self._encoding)


    def _get_content_bytes(self, offset1:int, size:int=0) -> bytes:
        _data = self._origin_data
        if size:
            _data_r = _data[offset1:offset1+size]
        else:
            _data_r = bytes()
        return _data_r

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

    def generate_json(self, output_path:str):
        import json
        # print(_struct)
        self._read_struct()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self._struct, f, ensure_ascii=False, indent=2)

    def get_all_string(self):
        position_spawnpoint_header = self._get_4bytes_to_uint(0x24)
        _type_bytes = self._get_content_bytes(position_spawnpoint_header, size=0x20)
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
        while(offset < size):
            while(end_bytes != utf16_byte):
                utf16_byte = self._origin_data[offset:offset+2]
                str_buffer.append(utf16_byte)
                offset += 2
            bytes_ = b''.join(str_buffer)
            str_ = bytes_.decode(encoding=self._encoding, errors='ignore')
            self._original_str_list.append(str_)
            str_buffer.clear()
            utf16_byte = b''
        return self._original_str_list

def run_main():
    import sys, time
    from pathlib import Path
    if len(sys.argv) == 1:
        print('RMPA file required!')
        time.sleep(3)
        sys.exit()
    else:
        file_path = Path(sys.argv[1])

    if len(sys.argv) == 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = file_path.with_suffix('.json')

    if '.rmpa' == file_path.suffix.lower():
        print('working..')
        a = RMPAParse()
        a.read(file_path)
        a.generate_json(output_path)
        print('done!')

if __name__ == "__main__":
    run_main()
