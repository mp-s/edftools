import os
import struct
import bvm_model as mdl
'''
    构造header
    构造全局变量名称表
    构造函数名称表
    全局变量初始化部分
    编译后字节码部分
    string表1部分(bytecode pushstr)
    string表2部分(global var name, func name)
    函数传参表部分
    类名部分
    最后的四字节补全
    最后的16字节补全
'''


class BVMGenerate(object):
    '''
        剥离 注释
        处理 name指令
        处理 类名         带类名函数标记
        处理 函数名, 类标记, 传参       非跳转点
        处理 strintable   string转操作数
        编译字节码        获取长度
        处理 跳转点 !!    跳转点转操作数
        写入字节码
        完成整个文件-->>>
    '''
    def __init__(self, debug_flag: bool = False):
        # self._trimed_data = None
        self._debug_flag = debug_flag
        self._named_fn_accept_num = {}
        self._named_fn_arg_types_dict = {}

    def _trim_comments(self, _data: list) -> list:
        ''' 去除所有注释部分, 有名函数传参注释记录 '''
        def trim_line_comment (line):
            if '//' in line:
                # 非函数传参部分的注释清洗 //
                return line.split('//')[0].rstrip()
            elif '/-' in line:
                # 带函数传参注释提取传参部分 /-
                # SceneEffect_Snow:   /- SceneEffect_Snow(float, float, int, float)
                func_line, func_arg = line.split('/-')          # ['SceneEffect_Snow:   ', ' SceneEffect_Snow(float, float, int, float)']
                func_line = func_line.strip()                   # 'SceneEffect_Snow:'
                func_arg = func_arg.strip()                     # 'SceneEffect_Snow(float, float, int, float)'
                func_arg_o_str = func_arg.split('(')[1]         # 'float, float, int, float)'
                func_arg_list = func_arg_o_str[:-1].split(',')  # ['float', ' float', ' int', ' float']
                func_args_num = 0 if '' == func_arg_list[0] else len(func_arg_list)              # 4
                _trimed_fn_name = func_line[:-1]
                self._named_fn_accept_num[_trimed_fn_name] = func_args_num
                self._named_fn_arg_types_dict[_trimed_fn_name] = [
                    mdl.func_arg_type_byte.get(_.strip())
                    for _ in func_arg_list
                ]                                               # [b'\x02', b'\x02', b'\x01', b'\x02']
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
        return _trimed_data[line_offset:]


    def _compile_global_variables(self) -> bytes:
        ''' 编译全局变量, 初始化变量的编译 '''
        flag_global_vars = True
        flag_constructor = False
        _global_var_list = [] # 纯名字 还需要生成一个地址表, 匹配打平后的数据
        self._gbl_var_rel_pos_list = [] # 地址表, 可统计长度, 可输出完成格式
        self._constructor_bytecode_list = []
        _gbl_var_rel_pos = 0

        # define global var, assign value
        for index, line in enumerate(self._trimed_data):

            if 'exit' in line:    # first exit break
                flag_constructor = False
                bytecode_head = index + 1
                self._asm_data = self._trimed_data[index+1:]
                return b''.join(_global_var_list)
                break

            if flag_global_vars:
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
            elif flag_constructor:
                opcode, operand = line.split()
                if '0x' in operand:
                    operand = bytes.fromhex(operand[2:])
                elif opcode == 'push':
                    operand_int = int(operand)
                    operand = operand_int.to_bytes(1, byteorder='little', signed=True)
                else:
                    operand_int = int(operand)
                    operand = operand_int.to_bytes(1, byteorder='little')
                line_bytecode = mdl.compiler_bytecode(opcode, operand)
                self._constructor_bytecode_list.append(line_bytecode)

            if '::' in line:
                self._class_name, func_name = line[:-1].split('::')
                if self._class_name in func_name: # Mission::Mission:
                    flag_constructor = True

    '''
        bytecode编译步骤:
        1. 字符串提取 转换成位置    done
        2. int, float提取           done
        3. hex提取                  done
        4. jmp点提取 转换为位置     done
    '''
    def _compile_str(self) -> bytes:
        ''' 提取字符串 合块 获得位置 应用入代码区 '''
        str_list = []
        for line in self._asm_data:
            if 'pushstr' in line:
                line_group = line.split()
                str_ = line_group[-1].strip('\"')
                if str_ not in str_list:
                    str_list.append(str_)

        bytes_str_tbl_1 = []    # generate string bytes
        current_str_offest = 0
        self._str_pos_table = {}
        for str_ in str_list:
            self._str_pos_table[str_] = current_str_offest
            _compiled_byte = str_.encode(encoding='utf-16le') + bytes(2)
            current_str_offest += len(_compiled_byte)   # next str position
            bytes_str_tbl_1.append(_compiled_byte)

        return b''.join(bytes_str_tbl_1)


    def _compile_operand(self):
        ''' 编译操作数为 bytes, 为下一步编译jmp获取长度用'''
        operands_use_uint = ['cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 
                            'cuscall3', 'loadabs', 'storeabs'] # unsigned int
        # operands_use_offset = ['jmp', 'call', 'jmpf', 'jmpt', 'jmpe', 'jmpne']
        def _c_operand(line:str):
            _group = line.split()
            if len(_group) == 2:    # 'location_xxx  :' glitch
                _opcode, _operand = _group
            else:   # no operand
                return [line.strip()]

            if 'pushstr' == _opcode:   # pushstr     "some_string"
                _str = _operand.strip('"')
                _str_pos = self._str_pos_table.get(_str)  # int
                length = 4 if _str_pos >> 16 else (2 if _str_pos >> 8 else 1)
                _compiled_byte = _str_pos.to_bytes(length, byteorder='little')
                return [_opcode, _compiled_byte]    # pushstr     (int)    --(0xHHHHHHHH)--

            elif _operand[0:2].lower() == '0x': # 0xhh
                _hex_str = _operand[2:]
                if len(_hex_str) & 0x1 != 0:
                    _hex_str = f'0{_hex_str}'   # 定长
                _compiled_byte = bytes.fromhex(_hex_str)[::-1]
                return [_opcode, _compiled_byte]

            elif _opcode == 'push' and _operand[-1] == 'f':
                float_ = float(_operand[:-1])
                _compiled_byte = struct.pack('<f', float_)
                return [_opcode, _compiled_byte]

            elif _opcode == 'push':
                int_ = int(_operand)
                if -128 < int_ <= 127:
                    length = 1
                # elif -32768 < int_ < 32767:
                else:
                    length = 2
                _compiled_byte = int_.to_bytes(length, byteorder='little', signed=True)
                return [_opcode, _compiled_byte]

            elif _opcode in operands_use_uint:
                int_ = int(_operand)
                length = 4 if int_ >> 16 else (2 if int_ >> 8 else 1)
                _compiled_byte = int_.to_bytes(length, byteorder='little')   # 不定长
                return [_opcode, _compiled_byte]

            else:
                return [line]

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
                # jump_mark_table[current_compiled_pos] = line[:-1].strip()
            else:
                _group = list_
                code_asm = _group[0].split()
                if 'jmp' in _group[0] or 'call' == code_asm[0]:
                    length_current_line = 3
                    list_ = list_[0].split()
                elif len(_group) == 1:
                    length_current_line = 1
                else:
                    length_opr = len(_group[1])
                    length_current_line = 1 + length_opr
                asm_pos_table[current_compiled_pos] = list_
                if jump_mark_flag:
                    self._jump_mark_table[jump_mark_name] = current_compiled_pos
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
                _compiled_operand = relative_pos.to_bytes(2, byteorder='little', signed=True)
                asm_pos_table[key] = [opcode, _compiled_operand]
        self._asm_data = list(asm_pos_table.values())

    def _compile_bytecode(self):
        ''' 全部转成bytecode 并打包 '''
        def _c_bcode(list_:list):
            if len(list_) == 1:
                return mdl.compiler_bytecode(list_[0])
            else:
                return mdl.compiler_bytecode(list_[0], list_[1])
        self._asm_data = list(map(_c_bcode, self._asm_data))

    def _compile_named_func(self):
        # 0x00 ~ 0x04
        self._named_fn_bytecode_positions = {}   # 块1表
        for k,v in self._jump_mark_table.items():   # remove 'location_xxx' mark
            if 'location' not in k:
                self._named_fn_bytecode_positions[k] = v

        self._named_fn_name_str_positions = {}   # 块2表

        name_str_pos_in_bytes = 0
        name_bytes_list = []
        
        _named_fn_block3_data = {}
        _named_fn_block4 = self._named_fn_accept_num    # 块4表
        # block3_pos_in_bytes = 0
        for k in self._named_fn_bytecode_positions.keys():
            _str_group = k.split('::')
            if len(_str_group) == 1:
                current_fn_name = k
                _named_fn_block3_data[k] = self._named_fn_arg_types_dict.get(k)
            elif len(_str_group) == 2 and self._class_name == _str_group[0]:    # Mission::Main
                current_fn_name = _str_group[1]
                _named_fn_block3_data[k] = self._class_name
            else:
                continue
            self._named_fn_name_str_positions[k] = name_str_pos_in_bytes
            byte_ = current_fn_name.encode(encoding='utf-16le') + bytes(2)
            name_bytes_list.append(byte_)
            name_str_pos_in_bytes += len(byte_)
        print()
        self._string_table2 = b''.join(name_bytes_list)

        self._named_fn_block3_positions = {}     # 块3表
        block3_pos_in_bytes = 0
        block3_cls_name_pos_flag = 0
        _block3_list = []
        for k,v in _named_fn_block3_data.items():
            if v == [None]:
                continue
            elif type(v) == list:
                self._named_fn_block3_positions[k] = block3_pos_in_bytes
                byte_ = b''.join(v)

                block3_pos_in_bytes += len(byte_)
                _block3_list.append(byte_)
            elif v == self._class_name:
                byte_ = v.encode(encoding='utf-16le') + bytes(2)
                if byte_ in _block3_list:
                    self._named_fn_block3_positions[k] = block3_cls_name_pos_flag
                else:
                    self._named_fn_block3_positions[k] = block3_pos_in_bytes
                    block3_cls_name_pos_flag = block3_pos_in_bytes

                    block3_pos_in_bytes += len(byte_)
                    _block3_list.append(byte_)
            else:
                pass
        self._fn_arg_bytes = b''.join(_block3_list)
        print()
        # func_name_chunk_list = []
        # for k, v in _named_fn_bytecode_positions.items():
        #     #  构建0x10数据
        #     _1 = v.to_bytes(4, byteorder='little')
        #     name_str_pos = _named_fn_name_str_positions.get(k, 0)
        #     _2 = name_str_pos.to_bytes(4, byteorder='little')
        #     arg_pos = _named_fn_block3_positions.get(k, 0)
        #     _3 = arg_pos.to_bytes(4, byteorder='little')
        #     _num = _named_fn_block4.get(k, 0)
        #     _4 = _num.to_bytes(4, byteorder='little')
        #     func_name_chunk_list.append(_1 + _2 + _3 + _4)
        # return b''.join(func_name_chunk_list)

    def read(self, file_path):
        with open(file=file_path, mode='r', encoding='utf-8') as f:
            file_data = f.readlines()
        self._trimed_data = self._trim_comments(file_data)

    def _generate_target(self):
        ''' 生成整个文件 '''
        bytes_head_type = b'BVM '
        bytes_head_type2 = bytes([0x50, 0, 0, 0]) # 0x50
        bytes_head_s1 = bytes(8)
        # 0x10
        bytes_head_s2 = b'\x38\x01\x15\x01\x02\x00\x00\x00'
        global_vars_num = len(self._gbl_var_rel_pos_list)
        global_vars_ofs = 0x50  # default
        # 0x20
        func_names_num = len(self._named_fn_bytecode_positions)
        func_names_ofs = global_vars_ofs + (global_vars_num * 0x04)
        stack1_size = int.to_bytes(512, 4, byteorder='little')
        stack2_size = int.to_bytes(512, 4, byteorder='little')
        # 0x30
        bytes_constructor_offset = func_names_ofs + (func_names_num * 0x10)
        bytes_main_offset = None
        bytes_strtbl_offset = None
        bytes_clsname_offset = None
        # 0x40
        bytes_static1 = bytes(4)
        bytes_padding4_size = None
        bytes_static2 = bytes_static1
        bytes_padding16_size = None
        # 0x50
        global_vars_bytes = {}
        func_names_bytes = {}
        construct_bytes = {}
        bytecode_bytes = {}
        str_table1_bytes = {}
        str_table2_bytes = {}
        str_table3_bytes = {}
        func_args_cls_types = {}
        # class_str_bytes = {}

    def debug_file(self, file_path = None):
        # print(self._asm_data)
        with open('q:\debug.asm', 'wb') as f:
            f.write(b''.join(self._asm_data))

    def build_file(self, file_path):
        bytes_buffer = b''

        with open(file=file_path, mode='wb') as f:
            f.write()

if __name__ == "__main__":
    p = BVMGenerate()
    p.read('q:/output.asm')
    p._compile_global_variables()
    p._compile_str()
    p._compile_operand()
    p._compile_jmp()
    p._compile_bytecode()
    p._compile_named_func()
    p.debug_file()