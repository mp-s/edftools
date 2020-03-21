import struct, re

pattern = re.compile(r'[\.]')


def wa():
    print('\t\t输入s结束程序', '\t\t浮点数必须带点号', '\t\t输入r切换大小端', sep='\n')


little_endian = False


def c_e(endian):
    print(f'\t当前字节序为:{endian}')


wa()
c_e('big')
while True:
    expression_str = input("FloatToHex> ")
    if ('s' == expression_str):
        break
    elif ('r' == expression_str):
        endian = 'little' if little_endian else 'big'
        little_endian = not little_endian
        c_e(endian)
        continue
    elif ('' == expression_str):
        continue
    expression_str = re.sub(r'[^0-9a-f\-\.]', '', expression_str)

    if little_endian:
        pack_str = '<f'
    else:
        pack_str = '>f'
    if '.' in expression_str:
        exp = float(expression_str)
        print(struct.pack(pack_str, exp).hex())
    else:
        try:
            exp = bytes.fromhex(expression_str)
            print(struct.unpack(pack_str, exp)[0])
        except:
            wa()