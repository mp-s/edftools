import json, struct

class RMPAGenerate:

    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(file_path, 'r', encoding='utf-8') as f:
            self._data_dict = json.load(f)
        # self._get_preprocess_result()
        self.pre = RMPAJsonPreprocess(self._data_dict)
        # self._name_string_table = pre.fixed_name_table_position_table
        # self._name_bytes = pre.name_table_bytes
        # self._base_data_count_table = pre.base_data_count_table

    def _build_type_block(self, type_name, type_dict):
        #  子头个数
        # 第一个子头偏移 默认 0x20
        # 空字符串偏移 
        type_group_name = type_dict.get('type group name')
        type_group_header_abs_position = self._get_type_header_abs_pos(type_name)
        sub_groups = type_dict.get('sub groups')
        sub_groups_count = len(sub_groups)

        type_header_block_bytes = self._build_type_header_block(
                type_group_name, sub_groups_count, type_group_header_abs_position)
        # sub_groups_start_position = 0x20

        sub_groups_header_bytes_list = []
        sub_group_datas_bytes_list = []
        sub_groups_abs_start_pos = type_group_header_abs_position + 0x20      # 多type时非固定
        for index, sub_group_item in enumerate(sub_groups):
            # self._build_sub_header()
            # 需要知道自己位置
            sub_dict = sub_group_item
            sub_group_name = sub_dict.get('sub group name')
            base_groups_list = sub_dict.get('base data')
            base_item_count = len(base_groups_list)

            self_head_abs_pos = sub_groups_abs_start_pos + index * 0x20
            _2_name_pos_int = self.pre.fixed_name_table_position_table.get(sub_group_name) - self_head_abs_pos

            remain_sub_groups_count = sub_groups_count - index
            remain_sub_groups_size = remain_sub_groups_count * 0x20
            before_groups_count = sum(self.pre.base_data_count_table.get(type_name)[:index]) # spawnpoint
            single_data_block_size = 0
            if type_name == 'spawnpoint':
                single_data_block_size = 0x40
                _fn = self._build_spawnpoint_block
            elif type_name == 'shape':
                single_data_block_size = 0x70
                _fn = self._build_shape_block
            before_base_data_groups_size = single_data_block_size * before_groups_count
            self_data_blk_pos = remain_sub_groups_size + before_base_data_groups_size

            sub_groups_header_bytes_list.append(
                b''.join([
                    bytes(0x14),
                    int_to_4bytes(_2_name_pos_int),
                    int_to_4bytes(base_item_count),
                    int_to_4bytes(self_data_blk_pos),
                ])
            )

            base_data_abs_start_pos = self_head_abs_pos + self_data_blk_pos
            _b = self._build_sub_group_base_block_data(type_name, base_data_abs_start_pos, base_groups_list)
            sub_group_datas_bytes_list.append(_b)
            # for index, base_item in enumerate(base_groups_list):
            #     if _fn:
            #         sub_group_datas_bytes_list.append(_fn(
            #                 base_item,
            #                 base_data_abs_start_pos + index * single_data_block_size))

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
        _type_name_abs_pos = self.pre.fixed_name_table_position_table.get(type_str_name, type_header_abs_pos)
        _bytes_0x18 = int_to_4bytes(_type_name_abs_pos - type_header_abs_pos)
        block_bytes = b''.join([
            _bytes_0x00, int_to_4bytes(0x20), bytes(8),
            bytes(8), _bytes_0x18, bytes(4)
        ])
        return block_bytes

    def _get_type_header_abs_pos(self, type_name):
        size = 0
        file_header_size = 0x30
        for _t_name, list_ in self.pre.base_data_count_table.items():
            if type_name == _t_name:
                break
            size += self.pre.type_block_size_predict(_t_name)
        return size + file_header_size



    def _build_spawnpoint_block(self, base_dict:dict, abs_pos_start:int) -> bytes:
        name_str = base_dict.get('name')
        pos1 = base_dict.get('positions_1')
        pos1_float_lst = list(map(float, pos1))
        pos2 = base_dict.get('positions_2')
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
        _6_bytes = self.pre.fixed_name_table_position_table.get(name_str) - abs_pos_start
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

    def _build_shape_block(self, base_dict:dict, abs_pos_start:int):
        # shape setup: 
        # 0x08  shape's type name
        # 0x10  shape's define name
        # 0x24 = 0x18 shape's size data position 
        # (0x30 * setup length + 0x10 * index)
        pass

    def _build_sub_group_base_block_data(self, type_name:str, group_start_pos:int, base_data_list:list) -> bytes:
        # (type_name, base_data_abs_start_pos, base_groups_list)
        # 名字字符串最后计算偏移
        # 生成rmpa id标识
        _main_group_data_list = []
        _extra_one_data_list = []
        if type_name == 'spawnpoint':
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x40 * index
                _main_group_data_list.append(self._build_spawnpoint_block(base_data_table, block_start_pos))
            return b''.join(_main_group_data_list)
        elif type_name == 'shape':
            shape_size_start_pos = 0x30 * len(base_data_list)
            for index, base_data_table in enumerate(base_data_list):
                block_start_pos = group_start_pos + 0x30 * index
                shape_type_name = base_data_table.get('shape type name')
                shape_type_name_pos = self.pre.fixed_name_table_position_table.get(shape_type_name, block_start_pos)
                shape_type_name_pos_byte = int_to_4bytes(shape_type_name_pos - block_start_pos)
                shape_def_name = base_data_table.get('shape var name')
                shape_def_name_pos = self.pre.fixed_name_table_position_table.get(shape_def_name, block_start_pos)
                shape_def_name_pos_byte = int_to_4bytes(shape_def_name_pos - block_start_pos)
                shape_size_pos = shape_size_start_pos + 0x10 * index
                shape_size_pos_bytes = int_to_4bytes(shape_size_pos)
                shape_setup_bytes = b''.join([
                    bytes(8), shape_type_name_pos_byte, bytes(4),
                    shape_def_name_pos_byte, bytes(4), shape_size_pos_bytes, bytes(4),
                    b'\0\0\0\1', shape_size_pos_bytes, bytes(8),
                ])

                shape_size_list = base_data_table.get('shape positions data')
                list_ = list(map(float_to_4bytes, (map(float, shape_size_list))))
                shape_size_data_bytes = b''.join([
                    list_[0], list_[1], list_[2], bytes(4),
                    list_[3], list_[4], list_[5], bytes(4),
                    list_[6], list_[7], bytes(8),
                    list_[8], list_[9], bytes(8),
                ])
                _main_group_data_list.append(shape_setup_bytes)
                _extra_one_data_list.append(shape_size_data_bytes)
            _1 = b''.join(_main_group_data_list)
            _2 = b''.join(_extra_one_data_list)
            return _1 + _2
        pass


    def run(self, file_path):

        some_bytes = b''
        some_type_names = ['route', 'shape', 'camera', 'spawnpoint']
        some_flags = [0, 0, 0, 0]
        some_header_pos = [0x30, 0x30, 0x30, 0x30]
        some_header_start_pos = 0x30
        for k, v in self._data_dict.items():
            block_bytes = self._build_type_block(k, v)
            some_bytes += block_bytes
            index = some_type_names.index(k)
            some_flags[index] = 1
            some_header_pos[index] = some_header_start_pos
            some_header_start_pos += len(block_bytes)
        _byte_rmpa_header = b'\0PMR\0\0\0\1'
        header_info_list = []
        for tuple_ in zip(some_flags, some_header_pos):
            header_info_list.append(int_to_4bytes(tuple_[0]) + int_to_4bytes(tuple_[1]))
        # _2_byte = b'\0\0\0\0\0\0\0\x30'
        # _3_byte = b'\0\0\0\x01\0\0\0\x30' + b'\0\0\0\0\0\0\0\x30'     # Change bytes
        # _4_byte = b'\0\0\0\x01\0\0\0\x30' +      # change bytes
        _byte_header = _byte_rmpa_header + b''.join(header_info_list) + bytes(8)

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
        self._read_node()

        self.fixed_name_table_position_table = self.abs_str_tbl()
        self.name_table_bytes = self.name_bytes()

    def name_bytes(self) -> bytes:
        if len(self.name_byte_list) == 0:
            self._read_node()
        return b''.join(self.name_byte_list)

    def _name_pos_prediction(self) -> int:
        _1_rmpa_header = 0x30
        _2_all_type_header = self._type_header_count * 0x20
        _3_all_sub_header = self._sub_header_count * 0x20

        # _4_route_block = sum(self.base_data_count_table.get('route'))
        self.shape_block_size = self.type_block_size_predict('shape')
        self.spawnpoint_block_size = self.type_block_size_predict('spawnpoint')
        abs_pos_start = _1_rmpa_header +\
            self.shape_block_size + self.spawnpoint_block_size
        print(hex(abs_pos_start))
        return abs_pos_start

    def type_block_size_predict(self, type_name) -> int:
        type_sub_groups_count_list = self.base_data_count_table.get(type_name, [0])
        type_header_size = 0x20
        sub_header_size = 0x20 * len(type_sub_groups_count_list)
        if type_name == 'shape':
            sub_data_size = (0x30 + 0x40) * sum(type_sub_groups_count_list)
        elif type_name == 'spawnpoint':
            sub_data_size = 0x40 * sum(type_sub_groups_count_list)
        else:
            sub_data_size = 0
        type_block_size = type_header_size + sub_header_size + sub_data_size
        return type_block_size

    def abs_str_tbl(self) -> dict:
        append_pos = self._name_pos_prediction()
        d_ = {k:v+append_pos for k,v in self._name_str_tbl.items()}
        return d_

    def _read_node(self, dict_:dict = None):
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

    def _read_list(self, type_name:str, list_:list):
        list_count = len(list_)
        if 'sub' in type_name:
            print('current sub header count:', list_count)
            self._sub_header_count += list_count
        elif 'base' in type_name:
            print('current base data count:', list_count)
            print(self._node_type_name)
            sub_groups_base = self.base_data_count_table.get(self._node_type_name, [])
            sub_groups_base.append(list_count)
            self.base_data_count_table[self._node_type_name] = sub_groups_base
        for item in list_:
            if type(item) == dict:
                self._read_node(item)

    def _append_str_to_tble(self, string:str):
        if string in self._name_str_tbl:
            return
        encoded_bytes = string.encode('utf-16be') + bytes(2)
        self._name_str_tbl[string] = self._string_offset
        self._string_offset += len(encoded_bytes)
        self.name_byte_list.append(encoded_bytes)

def int_to_4bytes(number:int) -> bytes:
    return number.to_bytes(4, byteorder='big')

def float_to_4bytes(number:float) -> bytes:
    return struct.pack('>f', number)

def test_preprocess():
    with open(r'D:\arena\EARTH DEFENSE FORCE 5\r\MISSION\DLC\DM024\MISSION.json', 'r', encoding='utf-8') as f:
        jsonstr = f.read()
    q = json.loads(jsonstr)
    p = RMPAJsonPreprocess(q)
    # for k in p._json_dict.keys():
    #     some_int = p._type_block_size_predict(k)
    #     print('k',k, 'value', some_int)
    # p.abs_str_tbl()
    # p.name_bytes()

def main():
    import os, sys
    if len(sys.argv) == 1:
        print('JSON file required!')
        input()
        sys.exit()
    else:
        file_path = sys.argv[1]
    _sp = os.path.splitext(file_path)

    if len(sys.argv) == 3:
        output_path = sys.argv[2]
    else:
        output_path = f'{_sp[0]}.rmpa'

    if '.json' == _sp[1].lower():
        print('working..')
        a = RMPAGenerate(file_path)
        # a.read(file_path)
        a.run(output_path)
        print('done!')

if __name__ == "__main__":

    # test_preprocess()
    main()
    # p = RMPAGenerate(r"D:\arena\EARTH DEFENSE FORCE 5\r\MISSION\DLC\DM022\MISSION.json")
    # p._get_str_table()
    # p.run(r"D:\arena\EARTH DEFENSE FORCE 5\r\MISSION\DLC\DM022\MISSIONtest2.rmpa")
