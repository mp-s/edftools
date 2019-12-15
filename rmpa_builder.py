import argparse
import json
import struct
from pathlib import Path

from rmpa_config import *


class RMPAGenerate:

    def __init__(self, debug_flag: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug_flag = debug_flag
        self._byteorder = 'big'

    def read(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            self._data_dict = json.load(f)
        self.pre = RMPAJsonPreprocess(self._data_dict, self._debug_flag)

    def _build_type_block(self, type_name, type_dict):
        #  子头个数
        # 第一个子头偏移 默认 0x20
        # 空字符串偏移
        type_group_name = type_dict.get(RmpaConfig.type_group_name)
        type_group_header_abs_position = self._get_type_header_abs_pos(
            type_name)
        sub_groups = type_dict.get(RmpaConfig.sub_enum_groups)
        sub_groups_count = len(sub_groups)
        if sub_groups_count == 0:
            return b''
        type_header_block_bytes = self._build_type_header_block(
            type_group_name, sub_groups_count, type_group_header_abs_position)
        # sub_groups_start_position = 0x20

        sub_groups_header_bytes_list = []
        sub_group_datas_bytes_list = []
        sub_groups_abs_start_pos = type_group_header_abs_position + 0x20      # 多type时非固定
        base_data_latest_padding_size = 0
        for index, sub_group_item in enumerate(sub_groups):
            # self._build_sub_header()
            # 需要知道自己位置
            sub_dict = sub_group_item
            sub_group_name = sub_dict.get(RmpaConfig.sub_enum_name)
            base_groups_list = sub_dict.get(RmpaConfig.base_data_list)
            base_item_count = len(base_groups_list)

            self_head_abs_pos = sub_groups_abs_start_pos + index * 0x20
            _2_name_pos_int = self.pre.name_abs_pos(
                sub_group_name) - self_head_abs_pos

            remain_sub_groups_count = sub_groups_count - index
            remain_sub_groups_size = remain_sub_groups_count * 0x20

            self_data_blk_pos = remain_sub_groups_size + base_data_latest_padding_size

            sub_groups_header_bytes_list.append(
                b''.join([
                    b'\x00\x01',
                    bytes(0x12),
                    int_to_4bytes(_2_name_pos_int),
                    int_to_4bytes(base_item_count),
                    int_to_4bytes(self_data_blk_pos),
                ])
            )

            base_data_abs_start_pos = self_head_abs_pos + self_data_blk_pos
            _b = self._build_sub_group_base_block_data(
                type_name, base_data_abs_start_pos, base_groups_list)
            sub_group_datas_bytes_list.append(_b)
            base_data_latest_padding_size += len(_b)

        _xx = [type_header_block_bytes]
        _xx.extend(sub_groups_header_bytes_list)
        _xx.extend(sub_group_datas_bytes_list)
        return b''.join(_xx)

    def _build_type_header_block(
            self,
            type_str_name: str,
            sub_dict_length: int,
            type_header_abs_pos: int) -> bytes:
        _bytes_0x00 = int_to_4bytes(sub_dict_length)
        _type_name_abs_pos = self.pre.name_abs_pos(
            type_str_name, type_header_abs_pos)
        _bytes_0x18 = int_to_4bytes(_type_name_abs_pos - type_header_abs_pos)
        block_bytes = b''.join([
            _bytes_0x00, int_to_4bytes(0x20), bytes(8),
            bytes(8), _bytes_0x18, bytes(4)
        ])
        return block_bytes

    def _get_type_header_abs_pos(self, type_name):
        size = 0
        file_header_size = 0x30
        for _t_name in self.pre.base_data_count_table:
            if type_name == _t_name:
                break
            size += self.pre.type_block_size_predict(_t_name)
        return size + file_header_size

    def _build_spawnpoint_block(self, base_dict: dict, abs_pos_start: int) -> bytes:
        sp = TypeSpawnPoint(self._byteorder)
        sp.from_dict(base_dict)
        sp.name_in_rmpa_pos = self.pre.name_abs_pos(
            sp.name) - abs_pos_start
        return sp.to_bytes_block()

    def _build_sub_group_base_block_data(self, type_name: str, group_start_pos: int, base_data_list: list) -> bytes:

        _main_group_data_list = []
        _extra_one_data_list = []
        if type_name == RmpaConfig.type_spawnpoint:
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x40 * index
                _main_group_data_list.append(
                    self._build_spawnpoint_block(base_data_table, block_start_pos))

        elif type_name == RmpaConfig.type_shape:
            shape_size_start_pos = 0x30 * len(base_data_list)
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x30 * index
                shape = TypeShape(self._byteorder)
                shape.from_dict(base_data_table)
                # shape name
                _name_rel_pos = self.pre.name_abs_pos(
                    shape.name, 0) - block_start_pos
                shape.name_in_rmpa_pos = _name_rel_pos
                # shape type name
                _type_rel_pos = self.pre.name_abs_pos(
                    shape.shape_type, 0) - block_start_pos
                shape.shape_type_in_rmpa_pos = _type_rel_pos
                # shape size data position
                shape.size_data_in_rmpa_pos = shape_size_start_pos + 0x10 * index
                # building block
                _main_group_data_list.append(shape.to_bytes_block())
                _extra_one_data_list.append(shape.to_bytes_block_size_data())

        elif type_name == RmpaConfig.type_route:
            wp_block_size = 0x3c * len(base_data_list)
            wp_blk_padding_size = (0x10 - wp_block_size % 0x10) % 0x10
            wp_extra_start_pos = wp_block_size + wp_blk_padding_size
            wp_extra_latest_end_pos = 0
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x3c * index
                wp = TypeWayPoint(self._byteorder)
                wp.from_dict(base_data_table)
                # waypoint name
                wp.name_in_rmpa_pos = self.pre.name_abs_pos(
                    wp.name, block_start_pos) - block_start_pos
                # waypoint extra position
                wp.next_wp_list_blk_in_rmpa_start_pos = wp_extra_start_pos + \
                    wp_extra_latest_end_pos - 0x3c * index
                wp_block_bytes = wp.to_bytes_block(index)
                _wp_extra_bytes = wp.to_bytes_block_extra()
                wp_extra_latest_end_pos += len(_wp_extra_bytes)
                _main_group_data_list.append(wp_block_bytes)
                _extra_one_data_list.append(_wp_extra_bytes)
            _main_group_data_list.append(bytes(wp_blk_padding_size))
        else:
            pass
        _1 = b''.join(_main_group_data_list)
        _2 = b''.join(_extra_one_data_list)
        return _1 + _2

    def generate_rmpa(self, file_path: Path):

        some_bytes = b''
        some_flags = []
        some_header_pos = []
        some_header_start_pos = 0x30
        for _t_n in RmpaConfig.compose_header:
            v = self._data_dict.get(_t_n)
            some_header_pos.append(some_header_start_pos)
            if v is None or _t_n == RmpaConfig.type_camera:
                some_flags.append(0)
                continue
            block_bytes = self._build_type_block(_t_n, v)
            if len(block_bytes) == 0:
                some_flags.append(0)
                continue
            some_bytes += block_bytes
            some_flags.append(1)

            some_header_start_pos += len(block_bytes)
        _byte_rmpa_header = b'\0PMR\0\0\0\1'
        header_info_list = []
        def ui_b(_n): return util.uint_to_4bytes(_n, self._byteorder)
        for _flag, _pos in zip(some_flags, some_header_pos):
            header_info_list.append(ui_b(_flag) + ui_b(_pos))

        with open(file_path, mode='wb') as f:
            f.write(_byte_rmpa_header)
            f.write(b''.join(header_info_list))
            f.write(bytes(8))
            f.write(some_bytes)
            f.write(self.pre.name_table_bytes)


class RMPAJsonPreprocess:
    def __init__(self, json_dict, debug_flag: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._json_dict = json_dict
        self._debug_flag = debug_flag

        self._name_str_tbl = {}
        self.name_byte_list = []
        self._string_offset = 0

        self._type_header_count = len(json_dict)
        self._sub_header_count = 0
        self._sp_data_count = 0
        self._node_type_name = None
        self.base_data_count_table = {}
        self._route_extra_data_size_list = []
        self._read_node(json_dict)

        self.__name_abs_pos = self._str_tbl_with_abs_pos()
        self.name_table_bytes = self.name_bytes()

    @property
    def name_abs_pos(self):
        return self.__name_abs_pos.get

    def name_bytes(self) -> bytes:
        if len(self.name_byte_list) == 0:
            self._read_node(self._json_dict)
        return b''.join(self.name_byte_list)

    def _name_tbl_start_pos_predict(self) -> int:
        _1_rmpa_header = 0x30

        self.route_block_size = self.type_block_size_predict(
            RmpaConfig.type_route)
        self.shape_block_size = self.type_block_size_predict(
            RmpaConfig.type_shape)
        self.spawnpoint_block_size = self.type_block_size_predict(
            RmpaConfig.type_spawnpoint)
        abs_pos_start = _1_rmpa_header + self.route_block_size +\
            self.shape_block_size + self.spawnpoint_block_size
        if self._debug_flag:
            print('first name offset: ', hex(abs_pos_start))
        return abs_pos_start

    def type_block_size_predict(self, type_name) -> int:
        type_sub_groups_count_list = self.base_data_count_table.get(type_name)
        if type_sub_groups_count_list is None:
            return 0
        type_header_size = 0x20
        sub_header_size = 0x20 * len(type_sub_groups_count_list)
        if type_name == RmpaConfig.type_shape:
            sub_data_size = (0x30 + 0x40) * sum(type_sub_groups_count_list)
        elif type_name == RmpaConfig.type_spawnpoint:
            sub_data_size = 0x40 * sum(type_sub_groups_count_list)
        elif type_name == RmpaConfig.type_route:
            sub_data_size = 0
            for route_base_count in type_sub_groups_count_list:
                sub_data_size += 0x3c * route_base_count
                padding_size = (0x10 - sub_data_size % 0x10) % 0x10
                sub_data_size += padding_size
            sub_data_size += sum(self._route_extra_data_size_list)
        else:
            return 0
        type_block_size = type_header_size + sub_header_size + sub_data_size
        return type_block_size

    def _waypoint_extra_blk_propress(self, base_data_list: list):
        for route_item in base_data_list:
            next_list = route_item.get(RmpaConfig.route_next_block, list())
            extra_sgo = route_item.get(RmpaConfig.waypoint_width)
            list_length = len(next_list)
            next_route_blk_size = (3 + list_length) // 4 * 4 * 0x04
            if extra_sgo:
                extra_sgo_size = 0x70
            else:
                extra_sgo_size = 0
            extra_size = next_route_blk_size + extra_sgo_size
            self._route_extra_data_size_list.append(extra_size)

    def _str_tbl_with_abs_pos(self) -> dict:
        append_pos = self._name_tbl_start_pos_predict()
        d_ = {k: v+append_pos for k, v in self._name_str_tbl.items()}
        return d_

    def _read_node(self, dict_: dict):
        key_list = [
            RmpaConfig.base_name,
            RmpaConfig.shape_type_name,
            RmpaConfig.sub_enum_name,
            RmpaConfig.type_group_name,
        ]
        for k, v in dict_.items():
            if type(v) == list:
                self._read_list(k, v)
            elif type(v) == dict:
                self._node_type_name = k
                self._read_node(dict_=v)
            elif k in key_list and type(v) == str:
                self._append_str_to_tble(v)

    def _read_list(self, type_name: str, list_: list):
        list_count = len(list_)
        if RmpaConfig.sub_enum_groups == type_name:
            if self._debug_flag:
                print('current sub header count:', list_count)
            self._sub_header_count += list_count
        elif RmpaConfig.base_data_list == type_name:
            if self._debug_flag:
                print('current base data count:', list_count)
                print(self._node_type_name)
            sub_groups_base = self.base_data_count_table.get(
                self._node_type_name, [])
            sub_groups_base.append(list_count)
            self.base_data_count_table[self._node_type_name] = sub_groups_base
            if self._node_type_name == RmpaConfig.type_route:
                self._waypoint_extra_blk_propress(list_)
                pass
        for item in list_:
            if type(item) == dict:
                self._read_node(item)

    def _append_str_to_tble(self, string: str):
        if string in self._name_str_tbl:
            return
        encoded_bytes = string.encode('utf-16be') + bytes(2)
        self._name_str_tbl[string] = self._string_offset
        self._string_offset += len(encoded_bytes)
        self.name_byte_list.append(encoded_bytes)


def int_to_4bytes(number: int) -> bytes:
    return number.to_bytes(4, byteorder='big')


def float_to_4bytes(number: float) -> bytes:
    return struct.pack('>f', number)


def main():
    args = parse_args()

    if args.source_path is None:
        str_ = input('drag file here and press Enter: ')
        source_path = Path(str_.strip('"'))
    else:
        source_path = Path(args.source_path)

    if args.destination_path:
        output_path = Path(args.destination_path)
    else:
        output_path = source_path.with_suffix('.rmpa')

    if '.json' == source_path.suffix.lower():
        print('working..')
        a = RMPAGenerate(args.debug)
        a.read(source_path)
        a.generate_rmpa(output_path)
        print('done!')


def parse_args():
    description = 'rmpa file builder'
    parse = argparse.ArgumentParser(description=description)

    help_ = 'input json file path'
    parse.add_argument('source_path', help=help_, nargs='?')
    help_ = 'output rmpa file path'
    parse.add_argument('destination_path', help=help_, nargs='?')

    help_ = 'enable debug mode'
    parse.add_argument('-d', '--debug', help=help_,
                       action='store_true', default=False)
    parse.add_argument('-t', action='store_true')

    return parse.parse_args()


if __name__ == "__main__":
    main()
