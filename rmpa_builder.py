import json, struct

class RMPAGenerate:

    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._str_table = {}
        self._str_byte_table = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            self._data_dict = json.load(f)

    def _build_type_header(self, type_name, type_dict):
        #  子头个数
        # 第一个子头偏移 默认 0x20
        # 空字符串偏移 
        type_group_name = type_dict.get('type group name')
        sub_groups = type_dict.get('sub groups')
        sub_groups_count = len(sub_groups)
        for sub_group_item in sub_groups:
            self._build_sub_header()
        pass
    
    def _build_sub_header(self, type_name, sub_dict):
        sub_group_name = sub_dict.get('sub group name')
        base_groups = sub_dict.get('base data')
        base_item_count = len(base_groups)
        for base_item in base_groups:
            self._build_base_data()
        pass

    def _build_spawnpoint_block(self, base_dict):
        name_str = base_dict.get('name')
        pos1 = base_dict.get('position_1')
        pos1_float = list(map(float, pos1))
        pos2 = base_dict.get('position_2')
        pos2_float = list(map(float, pos2))

        # generate simple block
        _1_bytes = bytes(0x0c)
        _2_bytes = None
        _3_bytes = bytes(4)
        _4_bytes = None
        _5_bytes = _1_bytes
        _6_bytes = str
        _7_bytes = bytes(8)
        
        # 构建自身块结束尾
        # rmpa id标识
        # 俩坐标
        # 字符串的长度和计算偏移
        pass

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

    def _append_str_table(self, str_:str):
        if self._str_tbl_pos :
            self._str_tbl_pos += 0
        else:
            self._str_tbl_pos = 0
        if str_ not in self._str_table:
            encoded_str_bytes = str_.encode(encoding='utf-16be')
            length_encoded = len(encoded_str_bytes)
            self._str_table[str_] = 0

    def _str_to_float(self, str_:str) -> float:
        if 'f' == str_[-1]:
            float_ = float(str_)
        else:
            float_ = 0.0
        return float_