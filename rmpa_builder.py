import json, struct

class RMPAGenerate:

    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(file_path, 'r', encoding='utf-8') as f:
            self._data_dict = json.load(f)

    def _build_type_block(self, type_name, type_dict):
        #  子头个数
        # 第一个子头偏移 默认 0x20
        # 空字符串偏移 
        type_group_name = type_dict.get('type group name')
        type_group_head_abs_position = 0x30
        sub_groups = type_dict.get('sub groups')
        sub_groups_count = len(sub_groups)
        sub_groups_start_position = 0x20

        sub_groups_bytes_list = []
        sub_group_datas_bytes_list = []
        sub_groups_abs_start_pos = 0x30 + 0x20
        for index, sub_group_item in enumerate(sub_groups):
            # self._build_sub_header()
            # 需要知道自己位置
            sub_dict = sub_group_item
            sub_group_name = sub_dict.get('sub group name')
            base_groups = sub_dict.get('base data')
            base_item_count = len(base_groups)

            _1_block = bytes(0x14)
            self_head_pos = sub_groups_abs_start_pos + index * 0x20
            _2_name_pos = self._name_string_table.get(sub_group_name) - self_head_pos
            _2_name_pos = _2_name_pos.to_bytes(4, byteorder='big')
            _3_block = base_item_count.to_bytes(4, byteorder='big')
            self_data_blk_pos = (sub_groups_count - index) * 0x20 + 0x40 * sum(self._base_data_count_table.get(type_name)[:index])
            _4_base_start_pos = self_data_blk_pos.to_bytes(4, byteorder='big')
            sub_groups_bytes_list.append(
                b''.join([
                    _1_block, _2_name_pos, _3_block, _4_base_start_pos
                ])
            )
            for index, base_item in enumerate(base_groups):
                sub_group_datas_bytes_list.append(self._build_spawnpoint_block(base_item, self_head_pos + self_data_blk_pos + index*0x40))
        
        _1_block = sub_groups_count.to_bytes(4, byteorder='big')
        _2_sub_start_pos = 0x20.to_bytes(4, byteorder='big')
        _3_block = bytes(0x10)
        _4_name_pos = self._name_string_table.get(type_group_name) - 0x30
        _4_name_pos = _4_name_pos.to_bytes(4, byteorder='big')
        _5_blk = bytes(0x04)

        type_byte_block = b''.join([
            _1_block, _2_sub_start_pos, _3_block,
            _4_name_pos, _5_blk
        ])
        
        _xx = [type_byte_block]
        _xx.extend(sub_groups_bytes_list)
        _xx.extend(sub_group_datas_bytes_list)
        return _xx

    def _build_sub_header(self, type_name, sub_dict):

        pass

    def _build_spawnpoint_block(self, base_dict, abs_pos_start):
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
        _6_bytes = self._name_string_table.get(name_str) - abs_pos_start
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

    def _build_shape_block(self):
        # shape setup: 
        # 0x04 
        pass

    def _build_base_data(self):
        # 名字字符串最后计算偏移
        # 生成rmpa id标识
        pass

    def _get_str_table(self):
        pre = RMPAJsonPreprocess(self._data_dict)
        self._name_string_table = pre.abs_str_tbl()
        self._name_bytes = pre.name_bytes()
        self._base_data_count_table = pre._base_data_count_table

    def run(self, file_path):
        self._get_str_table()
        some_bytes = b''
        for k, v in self._data_dict.items():
            some_bytes += b''.join(self._build_type_block(k, v))
        _1_byte = b'\0PMR\0\0\0\1'
        _2_byte = b'\0\0\0\0\0\0\0\x30'
        _3_byte = b'\0\0\0\0\0\0\0\x30\0\0\0\0\0\0\0\x30'
        _4_byte = b'\0\0\0\x01\0\0\0\x30\0\0\0\0\0\0\0\0'
        head_byte = _1_byte + _2_byte + _3_byte + _4_byte

        with open(file=file_path, mode='wb') as f:
            f.write(head_byte)
            f.write(some_bytes)
            f.write(self._name_bytes)

    def _str_to_float(self, str_:str) -> float:
        if 'f' == str_[-1]:
            float_ = float(str_)
        else:
            float_ = 0.0
        return float_

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
        self._base_data_count_table = {}
        self._read_node()

    def name_bytes(self) -> bytes:
        if len(self.name_byte_list) == 0:
            self._read_node()
        return b''.join(self.name_byte_list)

    def _name_pos_prediction(self) -> int:
        _1_rmpa_header = 0x30
        _2_all_type_header = self._type_header_count * 0x20
        _3_all_sub_header = self._sub_header_count * 0x20
        _4_sp_block = sum(self._base_data_count_table.get('spawnpoint')) * 0x40
        abs_pos_start = _1_rmpa_header + _2_all_type_header + \
            _3_all_sub_header + _4_sp_block
        print(abs_pos_start)
        return abs_pos_start

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
                if v not in self._name_str_tbl:
                    bytes_ = v.encode(encoding='utf-16be') + bytes(2)
                    self._name_str_tbl[v] = self._string_offset
                    length = len(bytes_)
                    self._string_offset += length
                    self.name_byte_list.append(bytes_)

    def _read_list(self, type_name:str, list_:list):
        list_count = len(list_)
        if 'sub' in type_name:
            print('current sub header count:', list_count)
            self._sub_header_count += list_count
        elif 'base' in type_name:
            print('current base data count:', list_count)
            print(self._node_type_name)
            sub_groups_base = self._base_data_count_table.get(self._node_type_name, [])
            sub_groups_base.append(list_count)
            self._base_data_count_table[self._node_type_name] = sub_groups_base
        for item in list_:
            if type(item) == dict:
                self._read_node(item)

if __name__ == "__main__":
    # with open(r'D:\arena\EARTH DEFENSE FORCE 5\r\MISSION\TEST\M9909\MISSION.json', 'r', encoding='utf-8') as f:
    #     jsonstr = f.read()
    # q = json.loads(jsonstr)
    # p = RMPAJsonPreprocess(q)
    # p.abs_str_tbl()
    # p.name_bytes()
    
    # p = RMPAGenerate(r'D:\arena\EARTH DEFENSE FORCE 5\r\MISSION\TEST\M9909\MISSION.json')
    # p._get_str_table()
    # p.run(r'q:/test.rmpa')
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