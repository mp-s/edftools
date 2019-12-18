import os

string_list = []
name_num_lst = []

class AWEParse:
    pass

class AWBParse:
    pass

class ExtractFileInfo:
    def __init__(self):
        super().__init__()
        self.file_num = None
        self.file_name = None
        self.file_content_pos = None

def read(awb_path: str):
    with open(file=awb_path, mode='rb') as f:
        _data = f.read()
    return _data


def byteToInt(bytes_: bytes) -> int:
    return int.from_bytes(bytes_, byteorder='little')


def parser_awe(bytes_data: bytes):
    current_offset = 0x08
    files_count_byte = bytes_data[current_offset:current_offset+4]
    file_count = byteToInt(files_count_byte)
    for pos in range(file_count):
        read_offset = pos * 4 + 0x14
        file_name_pos = bytes_data[read_offset:read_offset+4]
        name_pos_int = byteToInt(file_name_pos)
        name_str = _read_name(bytes_data, name_pos_int+read_offset)
        string_list.append(name_str)

        read_offset = pos * 2 + byteToInt(bytes_data[0x10:0x14])
        file_num_pos = bytes_data[read_offset: read_offset+2]
        file_num_int = byteToInt(file_num_pos)
        name_num_lst.append(file_num_int)
    return string_list


def read_4_byte(bytes_: bytes, offset: int) -> bytes:
    return bytes_[offset:offset+4]


def _read_name(data: bytes, offset: int) -> str:
    end_bytes = b'\x00'
    str_buffer = []
    name_byte = b''

    while(end_bytes != name_byte):
        name_byte = data[offset:offset+1]
        if end_bytes == name_byte:
            break
        str_buffer.append(name_byte)
        offset += 1

    bytes_ = b''.join(str_buffer)
    return bytes_.decode(encoding='ascii')


if __name__ == "__main__":
    import sys
    import time
    _awe_path = input('drag AWE file and press Enter :  ')
    _hca_path = input(
        'drag AWB extracted with "VGMToolbox" directory and press Enter :  ')
    print('-' * 20)
    _awe_path = _awe_path.strip('"')
    _hca_path = _hca_path.strip('"')
    print('source .AWE check : ', _awe_path)
    print('extracted path check : ', _hca_path)
    print('wait 4 seconds...')
    time.sleep(4)

    parser_awe(read(_awe_path))
    file_name_tbl = dict(zip(name_num_lst, string_list))

    path_lst = []
    placeholder_set = set()
    for root, dirs, files in os.walk(_hca_path):
        for file_name in files:
            _l = file_name.split('.')
            serial = _l.pop(-2)
            path_lst.append(serial)
            placeholder_set.add('.'.join(_l))
    print(f'file path num: {len(path_lst)} \n string list: {len(string_list)}')
    if len(path_lst) != len(string_list) and len(placeholder_set) != 1:
        print('文件夹内文件数量不匹配! 即将退出')
        time.sleep(5)
        sys.exit()
    placeholder = placeholder_set.pop()
    placeholder = placeholder.split('.')
    for _i, file_serial in enumerate(file_name_tbl):
        zero_str = '%05d' % file_serial
        _ll = placeholder[:]
        _ll.insert(-1, zero_str)
        test_old_filename = '.'.join(_ll)
        test_old_path = os.path.join(_hca_path, test_old_filename)
        _exist = os.path.exists(test_old_path)
        print('exists?', _exist, '\told path:', test_old_path)
        if _exist:
            new_name = file_name_tbl.get(file_serial) + '.hca'
            new_path = os.path.join(_hca_path, new_name)
            # print('new path: ', new_path)
            os.rename(test_old_path, new_path)
            # os.system(f'D:\\download\\hca.exe "{new_path}"')
