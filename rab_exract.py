import mmap
from pathlib import Path


class RABExtract:
    def __init__(self, file_path: Path):
        super().__init__()
        self._file_path = file_path

    def __enter__(self):
        '''
        @summary: 使用with语句是调用，会话管理器在代码块开始前调用，返回值与as后的参数绑定
        '''
        self.__fp = self._file_path.open('rb')
        self._file_mmap = mmap.mmap(
            self.__fp.fileno(), 0, access=mmap.ACCESS_READ)
        return self

    def __exit__(self, type_, value, traceback):
        '''
        @summary: 会话管理器在代码块执行完成好后调用（不同于__del__）(必须是4个参数)
        '''
        self._file_mmap.close()
        self.__fp.close()

    def read_header(self):
        header_bytes = self._file_mmap[0:0x28]
        if b'SSA\x00' == header_bytes[0:4]:
            self._byteorder = 'little'
            self._encoding = 'utf-16le'
        else:
            self._byteorder = 'big'
            self._encoding = 'utf-16be'
        self._file_count = util_read_4bytes_to_int(
            header_bytes, 0x14, byteorder=self._byteorder)
        # "result = 0x28"
        self._file_info_blk_pos = util_read_4bytes_to_int(
            header_bytes, 0x18, byteorder=self._byteorder)
        # unused for extract
        self._file_name_pos_lst_blk_start_pos = util_read_4bytes_to_int(
            header_bytes, 0x1c, byteorder=self._byteorder)
        self._dir_count = util_read_4bytes_to_int(
            header_bytes, 0x20, byteorder=self._byteorder)
        self._dir_name_pos_lst_blk_start_pos = util_read_4bytes_to_int(
            header_bytes, 0x24, byteorder=self._byteorder)

    def read_file_info(self):
        start_pos = self._file_info_blk_pos
        self.file_info_list = []
        for index in range(self._file_count):
            block_size = 0x20
            current_blk_rel_pos = index * block_size
            blk_start_pos = start_pos + current_blk_rel_pos
            file_info_block_bytes = self._read_contents_size(
                blk_start_pos, block_size)
            file_info = FileInfo(file_info_block_bytes, self._byteorder)
            file_info.file_name = self._get_string(
                file_info.name_rel_pos, index=blk_start_pos)
            self.file_info_list.append(file_info)
        self.file_info_list

    def read_dir_id(self):
        start_pos = self._dir_name_pos_lst_blk_start_pos
        self.dir_lst_name = []
        for index in range(self._dir_count):
            c_pos = start_pos + index * 0x04
            str_pos = util_read_4bytes_to_int(
                self._file_mmap, c_pos, byteorder=self._byteorder)
            self.dir_lst_name.append(self._get_string(str_pos, index=c_pos))
        self.dir_lst_name

    def extract(self, output_path_dir: Path = None):
        if output_path_dir == None:
            output_path_dir = self._file_path.with_suffix('.output')

        if not output_path_dir.is_dir():
            output_path_dir.mkdir()

        for file_info_item in self.file_info_list:
            e_filename = file_info_item.file_name
            e_contentpos = file_info_item.content_start_pos
            e_contentsize = file_info_item.file_size
            o_path = output_path_dir / e_filename
            if o_path.exists():
                continue
            with open(o_path, 'wb') as f:
                contents = self._read_contents_size(
                    e_contentpos, e_contentsize)
                f.write(contents)

    def _get_string(self, offset: int, index: int = 0) -> str:
        end_bytes = b'\x00\x00'
        str_buffer = []
        utf16_byte = b''
        offset = offset + index
        while(end_bytes != utf16_byte):
            utf16_byte = self._file_mmap[offset:offset+2]
            if end_bytes == utf16_byte:
                break
            str_buffer.append(utf16_byte)
            offset += 2
        bytes_ = b''.join(str_buffer)
        return bytes_.decode(encoding=self._encoding)

    def _read_contents_size(self, position, size):
        return self._file_mmap[position:position+size]


class FileInfo:
    def __init__(self, info_block_bytes: bytes, byteorder: str):
        super().__init__()
        self._block = info_block_bytes
        self._byteorder = byteorder
        self._block_parse()
        self.file_name = None
        self.file_content = None

    def _block_parse(self):
        ''' 0x20 length block parser '''
        self.name_rel_pos = util_read_4bytes_to_int(self._block, 0x00)
        self.file_size = util_read_4bytes_to_int(self._block, 0x04)
        self.root_dirs_identifer = [
            util_read_4bytes_to_int(self._block, 0x08),
            util_read_4bytes_to_int(self._block, 0x0c)
        ]
        self.file_time = self._block[0x10:0x18]
        self.content_start_pos = util_read_4bytes_to_int(self._block, 0x18)


def util_read_4bytes(bytes_blk: bytes, offset: int, start: int = 0) -> bytes:
    split1 = offset + start
    split2 = offset + start + 4
    return bytes_blk[split1:split2]


def util_read_4bytes_to_int(
        bytes_blk: bytes,
        offset: int,
        start: int = 0,
        byteorder='little') -> int:
    bytes_4 = util_read_4bytes(bytes_blk, offset, start)
    return int.from_bytes(bytes_4, byteorder=byteorder)


def run_main():
    with RABExtract(Path) as rab:
        rab.extract()


def run_test():
    input_path = Path(
        r"D:\arena\edf41\r\MISSION\ONLINEMISSIONIMAGE.RAB")
    with RABExtract(input_path) as rabObj:
        rabObj.read_header()
        rabObj.read_file_info()
        rabObj.read_dir_id()
        rabObj.extract()


if __name__ == "__main__":
    run_test()
