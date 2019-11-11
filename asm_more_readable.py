
import os, sys
from typing import List

def readable(path):
    with open(path, 'r', encoding='utf-8') as f:
        f_data = f.readlines()
    return additional_jmp_comments(f_data)

def additional_jmp_comments(file_data:List[str]):
    # jmp_loc_lst = []
    name_fn_tbl = {}
    for index, line in enumerate(file_data):
        if index > len(file_data) - 2:
            continue
        line = line.strip()
        if not line:
            continue
        if '/-' in line:
            line = line.split('/-')[0].strip()
        # print(line)
        if 'location_' not in line and line[-1] == ':':
            if 'call' in file_data[index+1] and 'exit' in file_data[index+2]:
                call_line = file_data[index+1].strip().split()[1]
                print(call_line, line)
                name_fn_tbl[call_line] = line

    def map_comments(line):
        if 'location_' in line:
            line = line.rstrip()
            if ':' in line[-1]:
                loc_key = line.strip(':').strip()
            elif len(line.split()) == 2:
                loc_key = line.split()[1]
            else:
                loc_key = ''
            print(loc_key)
            comments = name_fn_tbl.get(loc_key, '')
            if comments:
                line = line + '   // ' + comments + '\n'
            else:
                line = line + '\n'
        elif 'cuscall' in line or 'store' in line:
            line += '\n'
        return line
    final_data = list(map(map_comments, file_data))
    return final_data

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print('asm file required!')
        sys.exit()
    else:
        file_path = sys.argv[1]
    _sp = os.path.splitext(file_path)
    if len(sys.argv) == 3:
        output_path = sys.argv[2]
    else:
        output_path = f'{_sp[0]}.asm'
    if '.asm' == _sp[1].lower():
        print('working...')
        some = readable(file_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(some))
        print('done!')