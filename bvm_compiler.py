import os
import struct
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
func_arg_type_byte = {
    'int': b'\x01',
    'float': b'\x02',
    'string': b'\x03',
}

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
    def __init__(self):
        self._trimed_data = None


    def _trim_comments(self, _data: list) -> list:

        def trim_line_comment (line):
            if '//' in line:
                # 非函数传参部分的注释清洗 //
                return line.split('//')[0].rstrip()
            elif '/-' in line:
                # 带函数传参注释提取传参部分 /-
                func_name, func_arg = line.split('/-')
                func_name = func_name.strip()[:-1]
                func_arg_data = func_arg.split('(')[1][:-1].split(',')
                func_args_num = len(func_arg_data)
                func_args_bytes = [
                    func_arg_type_byte.get(_.strip())
                    for _ in func_arg_data
                ]
                return func_name
            else:
                return line.rstrip()
        return list(map(trim_line_comment, _data))
        

    def _compile_global_variables(self) -> list:
        flag_global_vars = True
        flag_constructor = False
        global_var_list = [] # 纯名字 还需要生成一个地址表, 匹配打平后的数据

        # define global var, assign value
        for index, line in enumerate(self._trimed_data):
            if flag_global_vars:
                if 'name' not in line:
                    flag_global_vars = False
                else:
                    global_var_name = line.split(' ')[-1]
                    global_var_list.append(global_var_name)
                    continue
            elif flag_constructor:
                pass # compile bytecode

            if '::' in line:
                class_name, func_name = line[:-1].split('::')
                if class_name in func_name: # Mission::Mission:
                    flag_constructor = True
            elif 'exit' in line:
                flag_constructor = False
                bytecode_head = index + 1
                self._asm_data = self._trimed_data[index+1:]
                return self._asm_data
                break

    '''
        Mission::Mission:
        push  0
        storeabs  0
        push  1
        neg  00
        storeabs  30
        exit
    '''

    '''
        bytecode编译步骤:
        1. 字符串提取 转换成位置    done
        2. int, float提取
        3. hex提取
        4. jmp点提取 转换为位置 ****
    '''
    def _compile_str(self) -> bytes:
        str_list = []
        str_pos_table = {}
        for line in self._trimed_data:
            if 'pushstr' in line:
                line_group = line.split()
                str_ = line_group[-1].strip('\"')
                str_list.append(str_)

        bytes_str_tbl_1 = []
        current_str_offest = 0
        for str_ in str_list:
            str_pos_table[str_] = current_str_offest
            _compiled_byte = str_.encode(encoding='utf-16le') + bytes(2)
            current_str_offest += len(_compiled_byte)   # next str position
            bytes_str_tbl_1.append(_compiled_byte)

        return b''.join(bytes_str_tbl_1)

        operands_use_uint = ['cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 
                            'cuscall3', 'loadabs', 'storeabs'] # unsigned int
        def _c_operand(line):
            _group = line.split()
            if len(_group) == 2:    # 'location_xxx  :' glitch
                _opcode, _operand = _group
            else:   # no operand
                return line
                _operand = None
            
            if 'location' in line and ':' in line:  # location_xxx :
                return line

            elif ':' in line[-1]:   # w/o "location" func name
                return line

            elif 'pushstr' == _opcode:   # pushstr     "some_string"
                _str = _operand.strip('"')
                _str_pos = str_pos_table.get(_str)  # int
                return f'{_opcode} {_str_pos}'    # pushstr     (int)    --(0xHHHHHHHH)--

            elif _operand[0:2].lower() == '0x': # 0xhh
                _hex_str = _operand[2:]
                if len(_hex_str) & 0x1 != 0:
                    _hex_str = f'0{_hex_str}'   # 定长
                _compiled_byte = bytes.fromhex(_hex_str)[::-1]
                return f'{_opcode} {_compiled_byte}'

            elif _opcode == 'push' and _operand[-1] == 'f':
                float_ = float(_operand[:-1])
                _compiled_byte = struct.pack('<f', float_)
                pass

            elif _opcode == 'push':
                int_ = int(_operand)
                if -128 < int_ <= 127:
                    length = 1
                # elif -32768 < int_ < 32767:
                else:
                    length = 2
                _compiled_byte = int_.to_bytes(length, byteorder='little', signed=True)
                return f'{_opcode} {_compiled_byte}'

            elif _opcode in operands_use_uint:
                int_ = int(_operand)
                length = 4 if int_ >> 16 else (2 if int_ >> 8 else 1)
                _compiled_byte = int_.to_bytes(length, byteorder='little')   # 不定长
                return f'{_opcode} {_compiled_byte}'
            else:
                return line

        self._trimed_data = list(map(_c_operand, self._trimed_data))


    operands_use_uint = ['cuscall', 'cuscall0', 'cuscall1', 'cuscall2', 'cuscall3'] # unsigned int
    operands_use_offset = ['jmp', 'call', 'jmpf', 'jmpt', 'jmpe', 'jmpne']
    def _compile_numbers(self):
        def _c_numbers(line:str):
            # 1 == 0x01
            if 'location' in line and ':' in line:  # location_xxx :
                return line
            elif ':' in line:
                return line
            else:
                _group = line.split()
                if len(_group) > 1:
                    if not (('pushstr' in line) or (_group[0] in self.operands_use_offset)):
                        number_str = _group[1]   # 数据操作
                        if number_str[-1] == 'f':
                            _float = float(number_str[:-1])  # float
                            compiled_operand = struct.pack('<f', _float)
                            pass
                        # elif number_str[0:2].lower() == '0x':   # 0xHHHH
                        #     _hex_str = number_str[2:]
                        #     compiled_operand_be = bytes.fromhex(_hex_str)
                        #     compiled_operand = compiled_operand_be[::-1] # little endian
                        #     pass
                        else:
                            _int = int(number_str)
                            compiled_operand = _int.to_bytes(byteorder='little')    # to_bytes need length
                            pass
                return _group[0], compiled_operand
        self._trimed_data = list(map(_c_numbers, self._trimed_data))

    def _compile_bytecode(self):
        def _c_bcode(line:list):
            _.get(list[0])
            pass

    def _compile_jmp(self):
        '''
            计算每行所需大小
            累计大小信息-> 当前行位置
            跳转点位置记录
            jmp语句位置与跳转点位置计算 出A
            jmp语句加入A
        '''
        def _c_jmp(line:str):
            if 'jmp' in line:
                pass
            elif ':' == line[-1]:
                pass
            else:
                return line
        pass

    def read(self, file_path):
        with open(file=file_path, mode='r', encoding='utf-8') as f:
            file_data = f.readlines()
        self._trimed_data = self._trim_comments(file_data)

    def _generate_target(self):
        bytes_head_type = b'BVM '
        bytes_head_type2 = bytes([0x50, 0, 0, 0]) # 0x50
        bytes_head_s1 = bytes(8)
        # 0x10
        bytes_head_s2 = b'\x38\x01\x15\x01\x02\x00\x00\x00'
        global_vars_num = None
        global_vars_ofs = None
        # 0x20
        func_names_num = None
        func_names_ofs = None
        stack1_size = int.to_bytes(512, 4, byteorder='little')
        stack2_size = int.to_bytes(512, 4, byteorder='little')
        # 0x30
        bytes_constructor_offset = None
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
        func_args_types = {}
        class_str_bytes = {}

    def build_file(self, file_path):
        bytes_buffer = b''

        with open(file=file_path, mode='wb') as f:
            f.write()