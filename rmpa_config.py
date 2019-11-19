#! python3
class Config:
    AMAZING_EXTRA_BIN_HEAD = b'SGO\x00\x02\x01\x00\x00\x01\x00\x00\x00 \x00\x00\x00\x01\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x004\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00'
    AMAZING_EXTRA_BIN_FOOT = b'\x08\x00\x00\x00\x00\x00\x00\x00r\x00m\x00p\x00a\x00_\x00f\x00l\x00o\x00a\x00t\x00_\x00W\x00a\x00y\x00P\x00o\x00i\x00n\x00t\x00W\x00i\x00d\x00t\x00h\x00\x00\x00'
    AMZING_EXTRA_SIZE = 0x66
    AMAZING_EXTRA_SIZE_ALIGNED = 0x70

    type_group_name = 'type group name'
    sub_enum_groups = 'sub groups'

    # sub enum group
    sub_enum_name = 'sub group name'
    base_data_list = 'base data'

    # types
    type_route = 'route'
    route_number = 'route number'
    route_position = 'positions'
    route_next_block = "current->next number"
    waypoint_width = 'rmpa_float_WayPointWidth'

    type_shape = 'shape'
    shape_type_name = 'shape type name'
    shape_variable_name = 'shape var name'
    shape_position_data = 'shape positions data'

    type_camera = 'camera'

    type_spawnpoint = 'spawnpoint'
    base_name = 'name'
    spawnpoint_pos_1 = 'positions_1'
    spawnpoint_pos_2 = 'positions_2'

    # debug
    type_chunk_end_position = 'type_chunk_end_position'
    current_block_position = 'block position'
    sub_header_count = 'numbers of enum sub header'
    base_data_count = 'base type count'
    route_next_block_pos = 'next blocks pos'
    route_sgo_block_pos = 'extra sgo pos'
    shape_size_pos = 'shape size data pos'

    # header groups
    compose_header = [type_route, type_shape, type_camera, type_spawnpoint]

cfg = Config