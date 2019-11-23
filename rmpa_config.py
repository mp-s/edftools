#! python3
import common_utils as util


class RmpaConfig:
    extra_sgo_head = b'SGO\x00\x02\x01\x00\x00\x01\x00\x00\x00 \x00\x00\x00\x01\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x004\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00'
    extra_sgo_foot = b'\x08\x00\x00\x00\x00\x00\x00\x00r\x00m\x00p\x00a\x00_\x00f\x00l\x00o\x00a\x00t\x00_\x00W\x00a\x00y\x00P\x00o\x00i\x00n\x00t\x00W\x00i\x00d\x00t\x00h\x00\x00\x00'
    extra_sgo_size = 0x66
    extra_sgo_size_aligned = 0x70
    extra_sgo_size_padding = extra_sgo_size_aligned - extra_sgo_size

    type_group_name = 'Type Group Name'
    sub_enum_groups = 'sub Enum Groups'

    # sub enum group
    sub_enum_name = 'sub Enum Group Name'
    base_data_list = 'base Data'

    # types
    type_route = 'route'
    route_number = 'WayPoint Number'
    route_position = 'positions'
    route_next_block = "next WayPoint Number List"
    waypoint_width = 'rmpa_float_WayPointWidth'
    # empty_waypoint_width = 'empty'

    type_shape = 'shape'
    shape_type_name = 'shape type name'
    shape_variable_name = 'shape var name'
    shape_position_data = 'shape positions data'

    type_camera = 'camera'

    type_spawnpoint = 'SpawnPoint'
    base_name = 'name'
    spawnpoint_pos_1 = 'positions_1'
    spawnpoint_pos_2 = 'positions_2'

    # debug
    type_chunk_end_position = 'typeChunkEndOffset'
    current_block_position = 'blockInRmpaOffset'
    sub_header_count = 'numbers of enum sub header'
    base_data_count = 'base type count'
    route_next_block_pos = 'next blocks pos'
    route_sgo_block_pos = 'extra sgo pos'
    shape_size_pos = 'shape size data pos'

    # header groups
    compose_header = [type_route, type_shape, type_camera, type_spawnpoint]


class TypeWayPoint:
    def __init__(self, byteorder: str):
        super().__init__()
        self._byteorder = byteorder
        self.name = None
        self.name_in_rmpa_pos = None
        self.position = None
        self.__wp_num = None

        self.next_wp_count = None
        self.next_wp_list_blk_in_rmpa_start_pos = None
        self.next_wp_list_blk_in_rmpa_end_pos = None
        self.next_wp_list = []

        self.extra_sgo_in_rmpa_start_pos = None
        self.extra_sgo_size = None
        self.wp_width = None

    @property
    def wp_number(self):
        return self.__wp_num

    def from_dict(self, dict_: dict):
        self.name = dict_.get(RmpaConfig.base_name)
        self.position = dict_.get(RmpaConfig.route_position)
        self.wp_width = dict_.get(RmpaConfig.waypoint_width)
        self.__wp_num = dict_.get(RmpaConfig.route_number)
        self.next_wp_list = dict_.get(RmpaConfig.route_next_block)

    def from_bytes_block(self, block: bytes):
        if len(block) != 0x3c:
            return None

        def g_i(pos: int) -> int:
            return util.uint_from_4bytes(util.get_4bytes(block, pos), self._byteorder)

        def g_f(pos: int) -> float:
            return util.float_from_4bytes(util.get_4bytes(block, pos), self._byteorder)

        self.name = None
        self.name_in_rmpa_pos = g_i(0x24)
        self.__wp_num = g_i(0x00)
        self.next_wp_count = g_i(0x04)
        self.position = [g_f(0x28), g_f(0x2c), g_f(0x30)]
        # extra block 1: next waypoint list
        self.next_wp_list_blk_in_rmpa_start_pos = g_i(0x08)
        self.next_wp_list_blk_in_rmpa_end_pos = g_i(0x10)
        # self.next_wp_list = []
        # extra block 2: sgo file
        self.extra_sgo_in_rmpa_start_pos = g_i(0x1c)
        self.extra_sgo_size = g_i(0x18)
        self.wp_width = None    # type: float

    def from_bytes_block_extra(self,
                               list_block: bytes = None,
                               sgo_block: bytes = None):
        if list_block:
            blk_size = self.next_wp_count * 0x04
            for pos in range(0, blk_size, 4):
                fb = util.get_4bytes(list_block, pos)
                _i = util.uint_from_4bytes(fb, self._byteorder)
                self.next_wp_list.append(_i)

        if sgo_block:
            sgo_head = util.get_4bytes(sgo_block, 0)
            byteorder = 'little' if sgo_head == b'SGO\0' else 'big'
            in_sgo_bytes = util.get_4bytes(sgo_block, 0x28)
            width_float = util.float_from_4bytes(in_sgo_bytes, byteorder)
            self.wp_width = width_float

    def to_dict(self, debug_flag: bool = False):
        if self.name is None:
            return dict()
        return {
            RmpaConfig.route_number: self.wp_number,
            RmpaConfig.base_name: self.name,
            RmpaConfig.route_position: self.position,
            RmpaConfig.waypoint_width: self.wp_width,
            RmpaConfig.route_next_block: self.next_wp_list,
        }

    def to_bytes_block(self, index: int):
        if False:
            return bytes()
        self.__wp_num = index  # type: int
        def i_b(_n): return util.uint_to_4bytes(_n, self._byteorder)
        name_pos_bytes = i_b(self.name_in_rmpa_pos)
        def _f(_n): return util.float_to_4bytes(float(_n), self._byteorder)
        wp_bytes = b''.join(map(_f, self.position))
        self.next_wp_count = len(self.next_wp_list)
        if self.next_wp_count == 0:
            next_wp_block_size = 0
        else:
            padding = (4 - self.next_wp_count % 4) % 4
            next_wp_block_size = (padding + self.next_wp_count) * 0x04

        if self.next_wp_list_blk_in_rmpa_start_pos is not None:
            self.next_wp_list_blk_in_rmpa_end_pos = next_wp_block_size + \
                self.next_wp_list_blk_in_rmpa_start_pos
        if self.wp_width is None:
            self.extra_sgo_size = 0
            self.extra_sgo_in_rmpa_start_pos = 0
        else:
            self.extra_sgo_size = RmpaConfig.extra_sgo_size
            self.extra_sgo_in_rmpa_start_pos = self.next_wp_list_blk_in_rmpa_end_pos

        block_bytes = b''.join([
            # 0x00
            i_b(self.__wp_num),
            i_b(self.next_wp_count),
            i_b(self.next_wp_list_blk_in_rmpa_start_pos),
            bytes(4),
            # 0x10
            i_b(self.next_wp_list_blk_in_rmpa_end_pos),
            bytes(4),
            i_b(self.extra_sgo_size),
            i_b(self.extra_sgo_in_rmpa_start_pos),
            # 0x20
            bytes(4),
            name_pos_bytes,
            wp_bytes,
            # 0x34
            bytes(8)
        ])
        return block_bytes

    def to_bytes_block_extra(self):
        if self.next_wp_count:
            def _i(_n): return util.uint_to_4bytes(_n, self._byteorder)
            next_wp_bytes = b''.join(map(_i, self.next_wp_list)) + \
                bytes((4 - self.next_wp_count % 4) % 4 * 0x04)
        else:
            next_wp_bytes = b''

        if self.wp_width is None:
            extra_sgo_bytes = b''
        else:
            self.wp_width = float(self.wp_width)
            extra_sgo_bytes = b''.join([
                RmpaConfig.extra_sgo_head,
                util.float_to_4bytes(self.wp_width, 'little'),
                RmpaConfig.extra_sgo_foot,
                bytes(RmpaConfig.extra_sgo_size_padding),
            ])
        return next_wp_bytes + extra_sgo_bytes


class TypeShape:
    def __init__(self, byteorder: str):
        super().__init__()
        self._byteorder = byteorder
        self.name: str = None
        self.name_in_rmpa_pos: int = None
        self.shape_type: str = None
        self.shape_type_in_rmpa_pos: str = None
        self.shape_size_data: list = None
        self.size_data_in_rmpa_pos: int = None
        # more detail in size_data
        self.position = None
        self.rectangle_size = None
        self.rectangle_extra = None
        self.shape_diameter = None
        self.shape_height = None

    def from_dict(self, dict_: dict):
        dg = dict_.get
        self.name = dg(RmpaConfig.base_name)
        self.shape_type = dg(RmpaConfig.shape_type_name)

        self.shape_size_data = dg(RmpaConfig.shape_position_data)

    def from_bytes_block(self, block: bytes):
        if len(block) != 0x30:
            return None

        def g_p(pos: int) -> int:
            return util.uint_from_4bytes(
                util.get_4bytes(block, pos), self._byteorder)
        self.name = None
        self.shape_type = None
        self.name_in_rmpa_pos = g_p(0x10)
        self.shape_type_in_rmpa_pos = g_p(0x08)
        self.size_data_in_rmpa_pos = g_p(0x24)

    def from_bytes_block_size_data(self, block: bytes):
        if len(block) != 0x40:
            return None

        def g_f(pos: int) -> float:
            return util.float_from_4bytes(
                util.get_4bytes(block, pos), self._byteorder)

        self.position = [g_f(0x00), g_f(0x04), g_f(0x08)]
        self.rectangle_size = [g_f(0x10), g_f(0x14), g_f(0x18)]
        self.rectangle_extra = g_f(0x24)
        self.shape_diameter = g_f(0x30)
        self.shape_height = g_f(0x34)
        self.shape_size_data = [
            self.position[0], self.position[1], self.position[2],
            self.rectangle_size[0], self.rectangle_size[1], self.rectangle_size[2],
            0.0, self.rectangle_extra,
            self.shape_diameter, self.shape_height,
        ]

    def to_dict(self, debug_flag: bool = False):
        if self.name is None or \
                self.shape_type is None or \
                self.shape_size_data is None:
            return dict()
        return {
            RmpaConfig.shape_type_name: self.shape_type,
            RmpaConfig.base_name: self.name,
            RmpaConfig.shape_position_data: self.shape_size_data,
        }

    def to_bytes_block(self):
        if self.name_in_rmpa_pos is None or \
                self.shape_type_in_rmpa_pos is None or \
                self.size_data_in_rmpa_pos is None:
            return bytes()

        def i_b(_n): return util.uint_to_4bytes(_n, self._byteorder)
        name_pos_bytes = i_b(self.name_in_rmpa_pos)
        shape_type_pos_bytes = i_b(self.shape_type_in_rmpa_pos)
        size_data_pos_bytes = i_b(self.size_data_in_rmpa_pos)
        block_bytes = b''.join([
            # 0x00
            bytes(8), shape_type_pos_bytes, bytes(4),
            # 0x10
            name_pos_bytes, bytes(4), size_data_pos_bytes, bytes(4),
            # 0x20
            b'\0\0\0\1', size_data_pos_bytes, bytes(8),
        ])
        return block_bytes

    def to_bytes_block_size_data(self):
        if self.shape_size_data is None:
            return bytes()

        def any_f_b(_n) -> bytes:
            return util.float_to_4bytes(float(_n), self._byteorder)
        list_ = list(map(any_f_b, self.shape_size_data))
        shape_size_data_bytes = b''.join([
            list_[0], list_[1], list_[2], bytes(4),
            list_[3], list_[4], list_[5], bytes(4),
            list_[6], list_[7], bytes(8),
            list_[8], list_[9], bytes(8),
        ])
        return shape_size_data_bytes


class TypeSpawnPoint:
    def __init__(self, byteorder: str):
        super().__init__()
        self._byteorder = byteorder
        self.name: str = None
        self.name_in_rmpa_pos: int = None
        self.is_at_position: list = None
        self.look_at_position: list = None

    def from_dict(self, dict_: dict):
        dg = dict_.get
        self.name = dg(RmpaConfig.base_name)

        # position? object?
        is_at_pos = dg(RmpaConfig.spawnpoint_pos_1)
        if isinstance(is_at_pos, list) and len(is_at_pos) == 3:
            self.is_at_position = list(map(float, is_at_pos))

        # target? point of view?
        look_at_pos = dg(RmpaConfig.spawnpoint_pos_2)
        if isinstance(look_at_pos, list) and len(look_at_pos) == 3:
            self.look_at_position = list(map(float, look_at_pos))

    def from_bytes_block(self, block: bytes):
        if len(block) != 0x40:
            return None

        def g_f(pos: int) -> float:
            return util.float_from_4bytes(
                util.get_4bytes(block, pos), byteorder=self._byteorder)

        self.is_at_position = [g_f(0x0c), g_f(0x10), g_f(0x14)]
        self.look_at_position = [g_f(0x1c), g_f(0x20), g_f(0x24)]
        self.name_in_rmpa_pos = util.uint_from_4bytes(
            util.get_4bytes(block, 0x34), self._byteorder)
        self.name = None

    def to_dict(self, debug_flag: bool = False):
        if self.name is None:
            return dict()
        return {
            RmpaConfig.base_name: self.name,
            RmpaConfig.spawnpoint_pos_1: self.is_at_position,
            RmpaConfig.spawnpoint_pos_2: self.look_at_position,
        }

    def to_bytes_block(self):
        if self.name_in_rmpa_pos is None:
            return bytes()

        def i_b(_n): return util.float_to_4bytes(_n, self._byteorder)
        name_pos_bytes = util.uint_to_4bytes(
            self.name_in_rmpa_pos, self._byteorder)
        is_x, is_y, is_z = tuple(map(i_b, self.is_at_position))
        look_x, look_y, look_z = tuple(map(i_b, self.look_at_position))
        block_bytes = b''.join([
            # 0x00
            bytes(0x0c),
            is_x,
            # 0x10
            is_y,
            is_z,
            bytes(4),
            look_x,
            # 0x20
            look_y, look_z,
            bytes(0x0c),
            # 0x34
            name_pos_bytes,
            bytes(0x08),
        ])
        return block_bytes
