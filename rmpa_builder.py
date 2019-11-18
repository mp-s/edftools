import argparse
import json
import struct
from pathlib import Path

import rmpa_config as cfg


class RMPAGenerate:

    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(file_path, 'r', encoding='utf-8') as f:
            self._data_dict = json.load(f)
        self.pre = RMPAJsonPreprocess(self._data_dict)
        self.debug_flag = False

    def _build_type_block(self, type_name, type_dict):
        #  子头个数
        # 第一个子头偏移 默认 0x20
        # 空字符串偏移
        type_group_name = type_dict.get(cfg.type_group_name)
        type_group_header_abs_position = self._get_type_header_abs_pos(
            type_name)
        sub_groups = type_dict.get(cfg.sub_enum_groups)
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
            sub_group_name = sub_dict.get(cfg.sub_enum_name)
            base_groups_list = sub_dict.get(cfg.base_data_list)
            base_item_count = len(base_groups_list)

            self_head_abs_pos = sub_groups_abs_start_pos + index * 0x20
            _2_name_pos_int = self.pre.fixed_name_table_position_table.get(
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
        _type_name_abs_pos = self.pre.fixed_name_table_position_table.get(
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
        name_str = base_dict.get(cfg.base_name)
        pos1 = base_dict.get(cfg.spawnpoint_pos_1)
        pos1_float_lst = list(map(float, pos1))
        pos2 = base_dict.get(cfg.spawnpoint_pos_2)
        pos2_float_lst = list(map(float, pos2))

        # generate simple block
        _1_bytes = bytes(0x0c)
        _2_bytes = b''
        for float_item in pos1_float_lst:
            _2_bytes += struct.pack('>f', float_item)
        _3_bytes = bytes(4)
        _4_bytes = b''
        for float_item in pos2_float_lst:
            _4_bytes += struct.pack('>f', float_item)
        _5_bytes = _1_bytes
        _6_bytes = self.pre.fixed_name_table_position_table.get(
            name_str) - abs_pos_start
        _6_bytes = _6_bytes.to_bytes(4, byteorder='big')
        _7_bytes = bytes(8)

        # 俩坐标
        # 字符串的长度和计算偏移
        return b''.join([
            _1_bytes, _2_bytes, _3_bytes, _4_bytes,
            _5_bytes, _6_bytes, _7_bytes
        ])

    def _build_route_block(self):
        # 0x0 当前编号                  必须
        # 0x4 多少个航点                必须
        # 0x8 控制下一位置数据块开始     必须
        # 0x10 数据块结束               必须
        # 0x14 rmpa id  不生成
        # 0x18 extra sgo size           有则必须
        # 0x1c extra sgo offset         有则必须
        # 0x20 名字长度                 不选择生成
        # 0x24 字符串偏移               必须
        # 0x28-0x34 坐标                必须
        pass

    def _build_shape_block(self, base_dict: dict, abs_pos_start: int):
        # shape setup:
        # 0x08  shape's type name
        # 0x10  shape's define name
        # 0x24 = 0x18 shape's size data position
        # (0x30 * setup length + 0x10 * index)
        pass

    def _build_sub_group_base_block_data(self, type_name: str, group_start_pos: int, base_data_list: list) -> bytes:
        # (type_name, base_data_abs_start_pos, base_groups_list)
        # 名字字符串最后计算偏移
        # 生成rmpa id标识
        _main_group_data_list = []
        _extra_one_data_list = []
        if type_name == cfg.type_spawnpoint:
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x40 * index
                _main_group_data_list.append(
                    self._build_spawnpoint_block(base_data_table, block_start_pos))
            # return b''.join(_main_group_data_list)
        elif type_name == cfg.type_shape:
            shape_size_start_pos = 0x30 * len(base_data_list)
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x30 * index
                shape_type_name = base_data_table.get(cfg.shape_type_name)
                shape_type_name_pos = self.pre.fixed_name_table_position_table.get(
                    shape_type_name, block_start_pos)
                shape_type_name_pos_byte = int_to_4bytes(
                    shape_type_name_pos - block_start_pos)
                shape_def_name = base_data_table.get(cfg.shape_variable_name)
                shape_def_name_pos = self.pre.fixed_name_table_position_table.get(
                    shape_def_name, block_start_pos)
                shape_def_name_pos_byte = int_to_4bytes(
                    shape_def_name_pos - block_start_pos)
                shape_size_pos = shape_size_start_pos + 0x10 * index
                shape_size_pos_bytes = int_to_4bytes(shape_size_pos)
                shape_setup_bytes = b''.join([
                    bytes(8), shape_type_name_pos_byte, bytes(4),
                    shape_def_name_pos_byte, bytes(
                        4), shape_size_pos_bytes, bytes(4),
                    b'\0\0\0\1', shape_size_pos_bytes, bytes(8),
                ])

                shape_size_list = base_data_table.get(cfg.shape_position_data)
                list_ = list(
                    map(float_to_4bytes, (map(float, shape_size_list))))
                shape_size_data_bytes = b''.join([
                    list_[0], list_[1], list_[2], bytes(4),
                    list_[3], list_[4], list_[5], bytes(4),
                    list_[6], list_[7], bytes(8),
                    list_[8], list_[9], bytes(8),
                ])
                _main_group_data_list.append(shape_setup_bytes)
                _extra_one_data_list.append(shape_size_data_bytes)

        elif type_name == cfg.type_route:
            route_block_size = 0x3c * len(base_data_list)
            route_block_padding_size = (0x10 - route_block_size % 0x10) % 0x10
            route_extra_start_pos = route_block_size + route_block_padding_size
            route_extra_latest_end_pos = 0
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x3c * index
                # 1
                # route_number = base_data_table.get('route number')
                route_number = index
                # 2
                route_name = base_data_table.get(cfg.base_name)
                route_name_pos = self.pre.fixed_name_table_position_table.get(
                    route_name, block_start_pos)
                route_name_pos -= block_start_pos
                # 3
                route_pos_data = base_data_table.get(cfg.route_position)
                route_pos_float_iter = map(float, route_pos_data)
                route_pos_bytes = b''.join(
                    map(float_to_4bytes, route_pos_float_iter))
                # 4
                _route_extra_bytes = b''
                next_route_list = base_data_table.get(cfg.route_next_block)
                # parser要调整数据 不能再固定了
                next_route_count = len(next_route_list)
                if next_route_count > 0:
                    next_route_block_size = 0x04 * next_route_count
                    next_route_block_padding_size = (
                        0x10 - next_route_block_size % 0x10) % 0x10
                    # result size
                    next_route_block_align_size = next_route_block_size + next_route_block_padding_size
                    # next_route_bytes = b''
                    _next_route_encoded_byte_iterator = map(
                        int_to_4bytes, next_route_list)
                    next_route_bytes = b''.join(
                        _next_route_encoded_byte_iterator)
                    # for nextRoute_number in next_route_list:
                    #     next_route_bytes += int_to_4bytes(nextRoute_number)
                    # result bytes
                    next_route_bytes += bytes(next_route_block_padding_size)
                else:
                    next_route_block_align_size = 0
                    next_route_bytes = b''
                # next_route_block_start_pos = 0
                # next_route_block_end_pos = next_route_block_start_pos + next_route_block_align_size
                # 5
                # sgo_start_pos = next_route_block_end_pos    # extra sgo process
                sgo_size = cfg.AMZING_EXTRA_SIZE   # padding data
                rmpa_waypoint_width = base_data_table.get(cfg.waypoint_width)
                if str(rmpa_waypoint_width).lower() != 'false':
                    no_sgo_flag = False
                    rmpa_waypoint_width = float(rmpa_waypoint_width)
                    width_bytes = struct.pack('<f', rmpa_waypoint_width)
                    extra_sgo_bytes = b''.join([
                        cfg.AMAZING_EXTRA_BIN_HEAD,
                        width_bytes,
                        cfg.AMAZING_EXTRA_BIN_FOOT,
                        bytes(cfg.AMAZING_EXTRA_SIZE_ALIGNED -
                              cfg.AMZING_EXTRA_SIZE)
                    ])
                else:
                    # padding zero
                    no_sgo_flag = True
                    extra_sgo_bytes = b''
                _route_extra_bytes = next_route_bytes + extra_sgo_bytes

                _extra_one_start_pos = route_extra_start_pos + \
                    route_extra_latest_end_pos - 0x3c * index
                _next_route_blk_end_pos = _extra_one_start_pos + next_route_block_align_size
                if no_sgo_flag:
                    extra_sgo_info_bytes = bytes(8)
                else:
                    extra_sgo_info_bytes = int_to_4bytes(cfg.AMZING_EXTRA_SIZE) +\
                        int_to_4bytes(_next_route_blk_end_pos)
                route_block_bytes = b''.join([
                    int_to_4bytes(route_number), int_to_4bytes(next_route_count), int_to_4bytes(
                        _extra_one_start_pos), bytes(4),   # 0x00
                    int_to_4bytes(_next_route_blk_end_pos), bytes(
                        4), extra_sgo_info_bytes,     # 0x10
                    bytes(4), int_to_4bytes(
                        route_name_pos), route_pos_bytes,   # 0x20 ~ 0x34
                    bytes(8)    # 0x34 ~
                ])
                route_extra_latest_end_pos += len(_route_extra_bytes)
                _main_group_data_list.append(route_block_bytes)
                # _main_group_data_list.append(bytes(route_block_padding_size))
                _extra_one_data_list.append(_route_extra_bytes)
            _main_group_data_list.append(bytes(route_block_padding_size))
        else:
            pass
        _1 = b''.join(_main_group_data_list)
        _2 = b''.join(_extra_one_data_list)
        return _1 + _2

    def run(self, file_path):

        some_bytes = b''
        some_type_names = cfg.compose_header
        some_flags = []
        # some_header_pos = [0x30, 0x30, 0x30, 0x30]
        some_header_pos = []
        some_header_start_pos = 0x30
        # for k, v in self._data_dict.items():
        for _t_n in some_type_names:
            k = _t_n
            v = self._data_dict.get(_t_n)
            some_header_pos.append(some_header_start_pos)
            if v is None or k == 'camera':
                some_flags.append(0)
                continue
            block_bytes = self._build_type_block(k, v)
            if len(block_bytes) == 0:
                some_flags.append(0)
                continue
            some_bytes += block_bytes
            some_flags.append(1)

            some_header_start_pos += len(block_bytes)
        _byte_rmpa_header = b'\0PMR\0\0\0\1'
        header_info_list = []
        for tuple_ in zip(some_flags, some_header_pos):
            header_info_list.append(int_to_4bytes(
                tuple_[0]) + int_to_4bytes(tuple_[1]))

        _byte_header = _byte_rmpa_header + \
            b''.join(header_info_list) + bytes(8)

        with open(file=file_path, mode='wb') as f:
            f.write(_byte_header)
            f.write(some_bytes)
            f.write(self.pre.name_table_bytes)


class RMPAJsonPreprocess:
    def __init__(self, json_dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._json_dict = json_dict

        self._name_str_tbl = {}
        self.name_byte_list = []
        self._string_offset = 0

        self._type_header_count = len(json_dict)
        self._sub_header_count = 0
        self._sp_data_count = 0
        self._node_type_name = None
        self.base_data_count_table = {}
        self._route_extra_data_size_list = []
        self._read_node()

        self.fixed_name_table_position_table = self.abs_str_tbl()
        self.name_table_bytes = self.name_bytes()

    def name_bytes(self) -> bytes:
        if len(self.name_byte_list) == 0:
            self._read_node()
        return b''.join(self.name_byte_list)

    def _name_pos_prediction(self) -> int:
        _1_rmpa_header = 0x30

        self.route_block_size = self.type_block_size_predict('route')
        self.shape_block_size = self.type_block_size_predict('shape')
        self.spawnpoint_block_size = self.type_block_size_predict('spawnpoint')
        abs_pos_start = _1_rmpa_header + self.route_block_size +\
            self.shape_block_size + self.spawnpoint_block_size
        print('first name offset: ', hex(abs_pos_start))
        return abs_pos_start

    def type_block_size_predict(self, type_name) -> int:
        type_sub_groups_count_list = self.base_data_count_table.get(type_name)
        if type_sub_groups_count_list is None:
            return 0
        type_header_size = 0x20
        sub_header_size = 0x20 * len(type_sub_groups_count_list)
        if type_name == 'shape':
            sub_data_size = (0x30 + 0x40) * sum(type_sub_groups_count_list)
        elif type_name == 'spawnpoint':
            sub_data_size = 0x40 * sum(type_sub_groups_count_list)
        elif type_name == 'route':
            # sub_data_size = 0x3c * sum(type_sub_groups_count_list)
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

    # def route_type_blk_size_predict(self, type_name='route') -> int:
    #     type_sub_groups_count_list = self.base_data_count_table.get(type_name, [0])
    #     sub_data_size = 0x3c * sum()
    #     pass

    def _route_type_extra_blk_propress(self, base_data_list: list):
        for route_item in base_data_list:
            next_list = route_item.get('current->next number')
            extra_sgo = route_item.get("rmpa_float_WayPointWidth")
            list_length = len(next_list)
            next_route_blk_size = (3 + list_length) // 4 * 4 * 0x04
            extra_sgo_size = 0 if str(extra_sgo).lower() == 'false' else 0x70
            extra_size = next_route_blk_size + extra_sgo_size
            self._route_extra_data_size_list.append(extra_size)

    def abs_str_tbl(self) -> dict:
        append_pos = self._name_pos_prediction()
        d_ = {k: v+append_pos for k, v in self._name_str_tbl.items()}
        return d_

    def _read_node(self, dict_: dict = None):
        if dict_ == None:
            dict_ = self._json_dict
        for k, v in dict_.items():
            if type(v) == list:
                self._read_list(k, v)
            elif type(v) == dict:
                self._node_type_name = k
                self._read_node(dict_=v)
            elif 'name' in k and type(v) == str:
                self._append_str_to_tble(v)

    def _read_list(self, type_name: str, list_: list):
        list_count = len(list_)
        if 'sub' in type_name:
            print('current sub header count:', list_count)
            self._sub_header_count += list_count
        elif 'base' in type_name:
            print('current base data count:', list_count)
            print(self._node_type_name)
            sub_groups_base = self.base_data_count_table.get(
                self._node_type_name, [])
            sub_groups_base.append(list_count)
            self.base_data_count_table[self._node_type_name] = sub_groups_base
            if self._node_type_name == 'route':
                self._route_type_extra_blk_propress(list_)
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


def test_preprocess():
    with open(r'D:\arena\EARTH DEFENSE FORCE 5\r\MISSION\DLC\DM024\MISSION.json', 'r', encoding='utf-8') as f:
        jsonstr = f.read()
    q = json.loads(jsonstr)
    p = RMPAJsonPreprocess(q)


def main():
    args = parse_args()
    source_path = Path(args.source_path)

    if args.destination_path:
        output_path = Path(args.destination_path)
    else:
        output_path = source_path.with_suffix('.rmpa')

    if '.json' == source_path.suffix.lower():
        print('working..')
        a = RMPAGenerate(source_path)
        a.run(output_path)
        print('done!')


def parse_args():
    description = 'rmpa file builder'
    parse = argparse.ArgumentParser(description=description)

    help_ = 'input json file path'
    parse.add_argument('source_path', help=help_)
    help_ = 'output rmpa file path'
    parse.add_argument('destination_path', help=help_, nargs='?')

    help_ = 'enable debug mode'
    parse.add_argument('-d', '--debug', help=help_,
                       action='store_true', default=False)
    parse.add_argument('-t', action='store_true')

    return parse.parse_args()


if __name__ == "__main__":
    main()
