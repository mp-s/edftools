#! python3

import struct
from pathlib import Path

from . import bvm_model as mdl


class BVMGenerate(object):
    jmp4_flag = False
    def __init__(self, debug_flag: bool = False):
        # self._trimed_data = None
        self._debug_flag = debug_flag
        self._named_fn_accept_num = {}
        self._named_fn_arg_types_dict = {}
        self._named_fn_ret_type_bytes = {}

    def _trim_comments(self, _data: list):
        ''' 去除所有注释部分, 有名函数传参注释记录 '''
        def trim_line_comment(line):
            if '//' in line:
                # 非函数传参部分的注释清洗 //
                return line.split('//')[0].rstrip()
            elif '/-' in line:
                # 带函数传参注释提取传参部分 /-
                # CruiseAndRespawn:   /- int(int, string, string, float)
                # ['CruiseAndRespawn:   ', ' int(int, string, string, float)']
                func_line, func_arg = line.split('/-')
                # 'CruiseAndRespawn:'
                func_line = func_line.strip()
                # 'int(int, string, string, float)'
                func_arg = func_arg.strip()
                _split_group = func_arg.split('(')
                # 'int'
                func_ret_type = _split_group[0]

                # 'float, float, int, float)'
                func_arg_o_str = _split_group[1]
                # ['float', ' float', ' int', ' float']
                func_arg_list = func_arg_o_str[:-1].split(',')
                func_args_num = 0 if '' == func_arg_list[0] else len(
                    func_arg_list)  # 4
                _trimed_fn_name = func_line[:-1]
                self._named_fn_accept_num[_trimed_fn_name] = func_args_num
                self._named_fn_arg_types_dict[_trimed_fn_name] = [
                    mdl.func_arg_type_byte.get(_.strip())
                    for _ in func_arg_list
                ]  # [b'\x02', b'\x02', b'\x01', b'\x02']
                self._named_fn_ret_type_bytes[
                    _trimed_fn_name] = mdl.func_arg_type_byte.get(
                        func_ret_type)
                return func_line
            else:
                return line.rstrip()

        _trimed_data = list(map(trim_line_comment, _data))
        line_offset = 0
        # triming file header empty line
        for index, line in enumerate(_trimed_data):
            if line.strip():
                line_offset = index
                break
        self._trimed_data = _trimed_data[line_offset:]
        if self._debug_flag:
            print("line_offset ", line_offset)

    def _compile_global_variables(self):
        ''' 编译全局变量, 初始化变量的编译 
        
        需要修改, name 可在任意地方调用.
        预想:
        寻找name + 寻找构造函数 + 寻找 pushstr
        name 转存后要去除 (会动 list 结构)
        构造函数需要开关 (:: 和下方相邻的 exit)
        pushstr 转存 string 内容和位置表
        '''
        flag_global_vars = True  # 全局变量名字
        flag_constructor = False  # 全局变量初始化(构造函数)
        _global_var_list = []  # 纯名字 还需要生成一个地址表, 匹配打平后的数据
        self._gbl_var_rel_pos_list = []  # 地址表, 可统计长度, 可输出完成格式
        self._constructor_bytecode_list = []
        _gbl_var_rel_pos = 0

        # define global var, assign value
        for index, line in enumerate(self._trimed_data):

            # 构造函数块完成
            if 'exit' == line.strip():    # first exit break
                self._constructor_bytecode_list.append(b'\x30')
                flag_constructor = False
                self._asm_data = self._trimed_data[index + 1:]
                self._global_var_bytes_list = _global_var_list
                break

            # name 表处理
            if flag_global_vars:
                # 列完 name
                if 'name' not in line:
                    flag_global_vars = False
                else:
                    global_var_name = line.split(' ')[-1]
                    global_var_byte = global_var_name.encode(encoding='utf-16le') +\
                        bytes(2)
                    _global_var_list.append(global_var_byte)
                    self._gbl_var_rel_pos_list.append(_gbl_var_rel_pos)
                    _gbl_var_rel_pos += len(global_var_byte)
                    continue

            # 构造函数处理
            elif flag_constructor:
                _l = line.split()
                if len(_l) == 1:
                    opcode = _l[0]
                    line_bytecode = mdl.compiler_bytecode(opcode)
                elif len(_l) == 0:
                    continue
                else:
                    opcode, operand, *_ = _l
                    if '0x' in operand:
                        operand = bytes.fromhex(operand[2:])
                    elif opcode == 'push':
                        if operand[-1] == 'f':
                            operand_float = float(operand[:-1])
                            operand = struct.pack('<f', operand_float)
                        else:
                            operand_int = int(operand)
                            operand = operand_int.to_bytes(1,
                                                           byteorder='little',
                                                           signed=True)
                    else:
                        operand_int = int(operand)
                        operand = operand_int.to_bytes(1, byteorder='little')
                    line_bytecode = mdl.compiler_bytecode(opcode, operand)
                self._constructor_bytecode_list.append(line_bytecode)

            # 识别构造函数开始
            if '::' in line:
                self._class_name, func_name = line[:-1].split('::')
                if self._class_name in func_name:  # Mission::Mission:
                    flag_constructor = True

    def _compile_str(self):
        '''
        提取pushstr内的字符串 合块 获得位置 应用入代码区

        pushstr opcode parse
        '''
        str_list = []
        for line in self._asm_data:
            if 'pushstr' in line:
                _ = line.split('pushstr')[-1]
                str_ = _.strip()[1:-1]
                if str_ not in str_list:
                    str_list.append(str_)

        self._str_tbl_bytes_list = []  # generate string bytes
        current_str_offest = 0
        self._str_pos_table = {}
        for str_ in str_list:
            self._str_pos_table[str_] = current_str_offest
            _compiled_byte = str_.encode(encoding='utf-16le') + bytes(2)
            current_str_offest += len(_compiled_byte)  # next str position
            self._str_tbl_bytes_list.append(_compiled_byte)
        if self._debug_flag:
            print("string len", len(self._str_tbl_bytes_list))


    def _compile_operand(self):
        ''' 编译操作数为 bytes, 为下一步编译jmp获取长度用'''
        operands_use_uint = [
            'cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 'cuscall3',
            'loadabs', 'storeabs'
        ]  # unsigned int

        def _c_operand(line: str):
            _group = line.split()  # 'pushstr "FOG 300"'  glitch
            if len(_group) == 2:  # 'location_xxx  :' glitch
                _opcode, _operand = _group
            elif len(_group) and _group[0] == 'pushstr':
                # 为了修复 pushstr "FOG 300" 问题, 另立条件
                _opcode = 'pushstr'
                _ = line.split('pushstr')[-1]
                _operand = _.strip()
            else:  # no operand 或者多个 operand
                return [line.strip()]

            # 这步 必有 opcode operand 两组
            if 'pushstr' == _opcode:  # pushstr     "some_string"
                _str = _operand.strip('"')
                _str_pos = self._str_pos_table.get(_str)  # int
                # length = 4 if _str_pos >> 16 else (2 if _str_pos >> 8 else 1)
                if -128 < _str_pos <= 127:
                    length = 1
                elif -32768 < _str_pos <= 32767:
                    length = 2
                else:
                    length = 4
                _compiled_byte = _str_pos.to_bytes(length, byteorder='little', signed=True)
                # pushstr     (int)    --(0xHHHHHHHH)--

            elif _operand[0:2].lower() == '0x':  # 0xhh
                _hex_str = _operand[2:]
                if len(_hex_str) & 0x1 != 0:
                    _hex_str = f'0{_hex_str}'  # 定长
                _compiled_byte = bytes.fromhex(_hex_str)[::-1]

            elif _opcode == 'push' and _operand[-1] == 'f':
                float_ = float(_operand[:-1])
                _compiled_byte = struct.pack('<f', float_)

            elif _opcode == 'push':
                int_ = int(_operand)
                if -128 < int_ <= 127:
                    length = 1
                else:
                    length = 2
                _compiled_byte = int_.to_bytes(length,
                                               byteorder='little',
                                               signed=True)

            elif _opcode in operands_use_uint:
                int_ = int(_operand)
                length = 4 if int_ >> 16 else (2 if int_ >> 8 else 1)
                _compiled_byte = int_.to_bytes(length,
                                               byteorder='little')  # 不定长

            else:
                return [line]

            return [_opcode, _compiled_byte]

        self._asm_data = list(map(_c_operand, self._asm_data))

    def _compile_jmp(self):
        ''' 编译jmp与call语句跳转为相对位置, 再转 bytes '''
        '''
            计算每行所需大小
            累计大小信息-> 当前行位置
            跳转点位置记录
            jmp语句位置与跳转点位置计算 出A
            jmp语句加入A
        '''
        current_compiled_pos = 0
        self._jump_mark_table = {}
        jump_mark_flag = False
        jump_mark_name = None
        asm_pos_table = {}
        for list_ in self._asm_data:
            if '' == list_[0]:
                continue
            if list_[0][-1] == ':':
                jump_mark_flag = True
                jump_mark_name = list_[0][:-1].strip()
            else:
                _group = list_
                code_asm = _group[0].split()
                if 'jmp' in _group[0] or 'call' == code_asm[0]:
                    if self.jmp4_flag:
                        length_current_line = 5
                    else:
                        length_current_line = 3
                    list_ = list_[0].split()
                elif len(_group) == 1:
                    length_current_line = 1
                else:
                    length_opr = len(_group[1])
                    length_current_line = 1 + length_opr
                asm_pos_table[current_compiled_pos] = list_
                if jump_mark_flag:
                    self._jump_mark_table[
                        jump_mark_name] = current_compiled_pos
                    jump_mark_name = None
                    jump_mark_flag = False
                current_compiled_pos += length_current_line

        for key, item in asm_pos_table.copy().items():
            _group = item
            opcode = _group[0]
            if 'jmp' in opcode or 'call' == opcode:
                loc_str = _group[1]
                mark_pos = self._jump_mark_table.get(loc_str, None)
                relative_pos = mark_pos - key
                if self.jmp4_flag:
                    _use_size = 4
                else:
                    _use_size = 2
                try:
                    _compiled_operand = relative_pos.to_bytes(_use_size,
                                                            byteorder='little',
                                                            signed=True)
                except OverflowError as err:
                    print("file size huge, maybe using '--jmp4' args to fix")
                asm_pos_table[key] = [opcode, _compiled_operand]
        self._asm_data = list(asm_pos_table.values())

    def _compile_bytecode(self):
        ''' 全部转成bytecode 并打包 '''
        def _c_bcode(list_: list):
            if len(list_) == 1:
                return mdl.compiler_bytecode(list_[0])
            else:
                return mdl.compiler_bytecode(list_[0], list_[1])

        self._main_bytecode_list = list(map(_c_bcode, self._asm_data))
        if self._debug_flag:
            print("main bytecode length", len(self._main_bytecode_list))

    def _compile_named_func(self):
        # 0x00 ~ 0x04
        self._named_fn_bytecode_positions = {}  # 块1表
        for k, v in self._jump_mark_table.items(
        ):  # remove 'location_xxx' mark
            if 'location' not in k:
                self._named_fn_bytecode_positions[k] = v

        self._named_fn_name_str_positions = {}  # 块2表

        name_str_pos_in_bytes = 0
        self._str_tbl3_list = []

        _named_fn_block3_data = {}
        _named_fn_block4 = self._named_fn_accept_num  # 块4表
        for k in self._named_fn_bytecode_positions.keys():
            # _str_group = k.split('::')
            # if len(_str_group) == 1:
            current_fn_name = k
            _named_fn_block3_data[k] = self._named_fn_arg_types_dict.get(k)
            # Mission::Main
            # elif len(_str_group) == 2 and self._class_name == _str_group[0]:
            #     current_fn_name = _str_group[1]
            #     _named_fn_block3_data[k] = self._class_name
            # else:
            #     continue
            self._named_fn_name_str_positions[k] = name_str_pos_in_bytes
            byte_ = current_fn_name.encode(encoding='utf-16le') + bytes(2)
            self._str_tbl3_list.append(byte_)
            name_str_pos_in_bytes += len(byte_)
        print()

        self._named_fn_block3_positions = {}  # 块3表
        block3_pos_in_bytes = 0
        # block3_cls_name_pos_flag = 0
        _block3_list = []
        for k, v in _named_fn_block3_data.items():
            if v == [None]:
                continue
            elif type(v) == list:
                self._named_fn_block3_positions[k] = block3_pos_in_bytes
                byte_ = b''.join(v)

                block3_pos_in_bytes += len(byte_)
                _block3_list.append(byte_)
            else:
                pass
        clsname_bytes = self._class_name.encode('utf-16le') + bytes(2)
        self._cls_name_bytes_len = len(clsname_bytes)
        _block3_list.append(clsname_bytes)
        self._fn_arg_bytes_list = _block3_list
        if self._debug_flag:
            print("named func bytes len", len(_block3_list))

    def _generate_target(self):
        ''' 生成整个文件 '''
        bytes_head_type = b'BVM '
        bytes_head_type2 = bytes([0x50, 0, 0, 0])  # 0x50
        bytes_head_s1 = bytes(8)
        # 0x10
        bytes_head_s2 = b'\x38\x01\x15\x01\x02\x00\x00\x00'
        global_vars_num = len(self._gbl_var_rel_pos_list)
        global_vars_ofs = 0x50  # default
        # 0x20
        func_names_num = len(self._named_fn_bytecode_positions)
        func_names_ofs = global_vars_ofs + (global_vars_num * 0x04)
        stack1_size = self._int_to_4bytes(512)
        stack2_size = self._int_to_4bytes(512)
        # 0x30
        bytes_constructor_offset = func_names_ofs + (func_names_num * 0x10)
        bytes_main_offset = None  # 构造体偏移 + 大小
        bytes_strtbl_offset = None  # 主脚本偏移 + 大小
        bytes_clsname_offset = None
        # bytes_strtbl2_offset = None # 主脚本用的 string 偏移 + 大小
        # 0x40
        bytes_static1 = bytes(4)
        bytes_padding4_size = None  # 0x04 - (bytesize % 0x04)
        bytes_static2 = bytes_static1
        # 0x10 - (bytesize % 0x10)  final file size
        bytes_padding16_size = None
        # 0x50
        global_vars_bytes = None
        func_names_bytes = None
        construct_bytes = None
        bytecode_bytes = None
        str_table1_bytes = None
        str_table2_bytes = None
        str_table3_bytes = None
        func_args_cls_types_bytes = None
        # class_str_bytes = {}

        # calculate bytes size and append bytes

        construct_bytes = b''.join(self._constructor_bytecode_list)
        constructor_size = len(construct_bytes)

        bytes_main_offset = bytes_constructor_offset + constructor_size
        bytecode_bytes = b''.join(self._main_bytecode_list)
        main_script_size = len(bytecode_bytes)

        bytes_strtbl_offset = bytes_main_offset + main_script_size
        str_table1_bytes = b''.join(self._str_tbl_bytes_list)
        str_tbl1_size = len(str_table1_bytes)

        # global var strings
        bytes_strtbl2_offset = bytes_strtbl_offset + str_tbl1_size
        str_table2_bytes = b''.join(self._global_var_bytes_list)
        bytes_strtbl3_offset = len(str_table2_bytes) + bytes_strtbl2_offset
        str_table3_bytes = b''.join(self._str_tbl3_list)
        fn_arg_types_offset = bytes_strtbl3_offset + len(str_table3_bytes)
        func_args_cls_types_bytes = b''.join(self._fn_arg_bytes_list)
        bytes_clsname_offset = fn_arg_types_offset + \
            len(func_args_cls_types_bytes) - self._cls_name_bytes_len
        if self._debug_flag:
            print("bytecode_bytes size", len(bytecode_bytes))
            print("str_tbl1_size", str_tbl1_size)
            print("bytes_strtbl2_offset", bytes_strtbl2_offset)
            print("bytes_strtbl3_offset", bytes_strtbl3_offset)
            print("fn_arg_types_offset", fn_arg_types_offset)
            print("bytes_clsname_offset", bytes_clsname_offset)

        # global var pos convert
        gbl_var_abs_pos_list = []
        for int_ in self._gbl_var_rel_pos_list:
            abs_pos = bytes_strtbl2_offset + int_
            abs_pos_byte = self._int_to_4bytes(abs_pos)
            gbl_var_abs_pos_list.append(abs_pos_byte)
        global_vars_bytes = b''.join(gbl_var_abs_pos_list)

        # func_name_bytes building
        named_fn_chunk_byte_list = []
        amazing_arg_pos = 0
        for k, v in self._named_fn_bytecode_positions.items():
            _1_rel_bytecode_pos = v
            _2_rel_str_pos = self._named_fn_name_str_positions.get(k, 0)
            _2_abs_str_pos = _2_rel_str_pos + bytes_strtbl3_offset
            _3_abs_arg_pos = amazing_arg_pos + fn_arg_types_offset
            _4_arg_nums = self._named_fn_accept_num.get(k, 0)
            amazing_arg_pos += _4_arg_nums
            _1 = self._int_to_4bytes(_1_rel_bytecode_pos)
            _2 = self._int_to_4bytes(_2_abs_str_pos)
            _3 = self._int_to_4bytes(_3_abs_arg_pos)
            ret_type = self._named_fn_ret_type_bytes.get(k)
            if ret_type:
                _4 = _4_arg_nums.to_bytes(
                    1, byteorder='little') + ret_type + bytes(2)
            else:
                _4 = self._int_to_4bytes(_4_arg_nums)
            named_fn_chunk_byte_list.append(b''.join([_1, _2, _3, _4]))
        func_names_bytes = b''.join(named_fn_chunk_byte_list)

        file_size = fn_arg_types_offset + len(func_args_cls_types_bytes)
        bytes_padding4_size = 0x04 - (file_size % 0x04) + file_size
        bytes_padding16_size = 0x10 - (file_size % 0x10) + file_size

        # convert bytes
        global_vars_num = self._int_to_4bytes(global_vars_num)
        global_vars_ofs = self._int_to_4bytes(global_vars_ofs)
        func_names_num = self._int_to_4bytes(func_names_num)
        func_names_ofs = self._int_to_4bytes(func_names_ofs)
        bytes_constructor_offset = self._int_to_4bytes(
            bytes_constructor_offset)
        bytes_main_offset = self._int_to_4bytes(bytes_main_offset)
        bytes_strtbl_offset = self._int_to_4bytes(bytes_strtbl_offset)
        bytes_clsname_offset = self._int_to_4bytes(bytes_clsname_offset)

        _lst = [
            # 0x00
            bytes_head_type,
            bytes_head_type2,
            # 0x08
            bytes_head_s1,
            # 0x10
            bytes_head_s2,
            global_vars_num,
            global_vars_ofs,
            # 0x20
            func_names_num,
            func_names_ofs,
            stack1_size,
            stack2_size,
            # 0x30
            bytes_constructor_offset,
            bytes_main_offset,
            # 0x38
            bytes_strtbl_offset,
            bytes_clsname_offset,
            bytes_static1,
            self._int_to_4bytes(bytes_padding4_size),
            bytes_static2,
            self._int_to_4bytes(bytes_padding16_size),
        ]
        header_bytes = b''.join(_lst)
        _lst2 = [
            header_bytes, global_vars_bytes, func_names_bytes, construct_bytes,
            bytecode_bytes, str_table1_bytes, str_table2_bytes,
            str_table3_bytes, func_args_cls_types_bytes
        ]
        full_bytes = b''.join(_lst2)
        if len(full_bytes) < bytes_padding16_size:
            padding = b'\xba' * (bytes_padding16_size - len(full_bytes))
            full_bytes = full_bytes + padding
        return full_bytes

    def _int_to_4bytes(self, number: int) -> bytes:
        return number.to_bytes(4, byteorder='little')

    def read(self, file_path):
        with open(file=file_path, mode='r', encoding='utf-8') as f:
            file_data = f.readlines()
        self._trim_comments(file_data)

    def debug_file(self, file_path=None):
        # print(self._asm_data)
        with open(file_path, 'wb') as f:
            f.write(b''.join(self._asm_data))

    def output_file(self, file_path: Path):
        self._compile_global_variables()
        self._compile_str()
        self._compile_operand()
        self._compile_jmp()
        self._compile_bytecode()
        self._compile_named_func()
        bytes_buffer = self._generate_target()

        with open(file_path, mode='wb') as f:
            f.write(bytes_buffer)


if __name__ == "__main__":
    from time import sleep
    print('none')
    sleep(4)
