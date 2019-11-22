#! python3
import common_utils as util


class Config:
    extra_sgo_head = b'SGO\x00\x02\x01\x00\x00\x01\x00\x00\x00 \x00\x00\x00\x01\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x004\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00'
    extra_sgo_foot = b'\x08\x00\x00\x00\x00\x00\x00\x00r\x00m\x00p\x00a\x00_\x00f\x00l\x00o\x00a\x00t\x00_\x00W\x00a\x00y\x00P\x00o\x00i\x00n\x00t\x00W\x00i\x00d\x00t\x00h\x00\x00\x00'
    extra_sgo_size = 0x66
    extra_sgo_size_aligned = 0x70

    type_group_name = 'type group Name'
    sub_enum_groups = 'sub groups'

    # sub enum group
    sub_enum_name = 'sub Enum Group Name'
    base_data_list = 'base Data'

    # types
    type_route = 'route'
    route_number = 'WayPointNumber'
    route_position = 'positions'
    route_next_block = "nextWayPointNumberList"
    waypoint_width = 'rmpa_float_WayPointWidth'
    empty_waypoint_width = 'empty'

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


cfg = Config


class TypeWayPoint:
    def __init__(self, debug_flag: bool = False):
        super().__init__()
        self._debug_flag = debug_flag

    def from_dict(self, dict_: dict):
        self.name = dict_.get(cfg.base_name)
        self.waypoint_postion = dict_.get(cfg.route_position)
        self.waypoint_width = dict_.get(cfg.waypoint_width)
        self.waypoint_number = dict_.get(cfg.route_number)
        self.waypoint_next_route_list = dict_.get(cfg.route_next_block)

    def from_bytes_block(self, block: bytes):

        pass


class TypeShape:
    def __init__(self, byteorder, debug_flag: bool = False):
        super().__init__()
        self._debug_flag = debug_flag
        self._byteorder = byteorder

    def from_dict(self, dict_: dict):
        dg = dict_.get
        self.name = dg(cfg.shape_variable_name)
        self.shape_type = dg(cfg.shape_type_name)

        self.shape_size_data = dg(cfg.shape_position_data)

    def from_bytes_block(self, block: bytes):
        if len(block) != 0x30:
            return None

        def g_p(pos: int) -> int:
            return util.uint_from_4bytes(util.get_4bytes(block, pos), self._byteorder)
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
                util.get_4bytes(block, pos), byteorder=self._byteorder)

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

    def generate_dict(self):
        return {
            Config.shape_type_name: self.shape_type,
            Config.shape_variable_name: self.name,
            Config.shape_position_data: self.shape_size_data,
        }


class TypeSpawnPoint:
    def __init__(self, byteorder, debug_flag: bool = False):
        super().__init__()
        self._debug_flag = debug_flag
        self._byteorder = byteorder

    def from_dict(self, dict_: dict):
        dg = dict_.get
        self.name = dg(cfg.base_name)
        # position? object?
        is_at_pos = dg(cfg.spawnpoint_pos_1)
        if isinstance(is_at_pos, list) and len(is_at_pos) == 3:
            self.is_at_position = list(map(float, is_at_pos))
        # target? point of view?
        look_at_pos = dg(cfg.spawnpoint_pos_2)
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
        self.name_in_rmpa_position = util.int_from_4bytes(
            util.get_4bytes(block, 0x34), self._byteorder)
        self.name = None

    def to_dict(self):
        if not self.name:
            return dict()
        return {
            Config.base_name: self.name,
            Config.spawnpoint_pos_1: self.is_at_position,
            Config.spawnpoint_pos_2: self.look_at_position,
        }

    def to_bytes_block(self):
        def i_b(num: float) -> bytes:
            return util.float_to_4bytes(num, self._byteorder)
        name_pos_bytes = util.int_to_4bytes(
            self.name_in_rmpa_position, self._byteorder)
        is_x, is_y, is_z = tuple(map(i_b, self.is_at_position))
        look_x, look_y, look_z = tuple(map(i_b, self.look_at_position))
        blk_bytes = b''.join([
            bytes(0x0c), is_x,
            is_y, is_z, bytes(4), look_x,
            look_y, look_z, bytes(0x0c),
            name_pos_bytes, bytes(0x08)
        ])
        return blk_bytes