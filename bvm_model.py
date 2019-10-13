
offset_list = {
    'pointer_list_count': 0x18,
    'pointer_list_index': 0x1c,
    'pointer_list2_count': 0x20,
    'pointer_list2_index': 0x24,
    'store_chunk_index': 0x30,
    'asm_code_chunk_index': 0x34,
    'string_chunk_index': 0x38,
    'class_name_index': 0x3c,
    'data_size_offset_index': 0x44,
    'data_align_index': 0x4c
}

asm_opcode = {
    # pop A
    # pop B
    # &A = B
    # push B 
    b'\x01': ('cvtstore', 1),

    b'\x02': ('pop', 0),
    b'\x03': ('pushtop', 0),

    # pop A
    # pop B
    # ***
    b'\x04': ('add', 1),    # push (A + B)
    b'\x05': ('sub', 1),    # push (A - B)
    b'\x06': ('mult', 1),   # push (A * B)
    b'\x07': ('div', 1),    # push (A / B)
    # pop A
    # pop B
    # mod 
    b'\x08': ('mod', 1),    # push (A % B)

    # stack first variable
    b'\x09': ('neg', 1),    # 1 -> -1 or -1 -> 1
    b'\x0a': ('inc', 1),    # ++
    b'\x0b': ('dec', 1),    # --

    # pop A
    # pop B
    # *** 
    b'\x0c': ('sar', 0),    # A >> B
    b'\x0d': ('sll', 0),    # A << B
    b'\x0e': ('and', 0),    # A & B
    b'\x0f': ('or', 0),     # A | B
    b'\x10': ('xor', 0),    # A ^ B
    # pop B
    b'\x11': ('not', 0),    # push (not B)
    
    b'\x12': ('ftoi', 0),   # float -> int 
    b'\x13': ('itof', 0),   # int -> float 
    # global vars
    b'\x14': ('loadabs', 0), b'\x54': ('loadabs', 1),
    # next at 33
    b'\x15': ('push', 0), b'\x55': ('push', 1), b'\x95': ('push', 2), b'\xd5': ('push', 4),
    # global vars
    b'\x16': ('storeabs', 0), b'\x56': ('storeabs', 1),
    # script-stack
    b'\x17': ('loadrel', 0), b'\x57': ('loadrel', 1),
    b'\x18': ('pushrel', 0), b'\x58': ('pushrel', 1), b'\x98': ('pushrel', 2),
    b'\x19': ('storerel', 0), b'\x59': ('storerel', 1),
    # push string address
    b'\x1a': ('pushstr', 0), b'\x5a': ('pushstr', 1), b'\x9a': ('pushstr', 2),
    # script-stack
    b'\x1b': ('addrel', 0), b'\x5b': ('addrel', 1), b'\x9b': ('addrel', 2),
    b'\x1c': ('subrel', 0), b'\x5c': ('subrel', 1),


    # pop B
    # pop A
    # test**(without testz)
    b'\x1d': ('testnand', 1),     # if A!=0 and B!=0 (push 1) else (push 0)
    b'\x1e': ('testor', 1),    # if A!=0 or B!=0 (push 1) else (push 0)
    b'\x1f': ('testz', 1),      # pop B, push !B
    b'\x20': ('testg', 1),      # if A < B  (push 1) else (push 0)
    b'\x21': ('testge', 1),     # if A <= B (push 1) else (push 0)
    b'\x22': ('teste', 1),      # if A == B (push 1) else (push 0)
    b'\x23': ('testne', 1),     # if A != B (push 1) else (push 0)
    b'\x24': ('testle', 1),     # if A > B  (push 1) else (push 0)
    b'\x25': ('testl', 1),      # if A >= B (push 1) else (push 0)

    # jump
    # pop A
    # jmp* location_xxx 
    b'\x26': ('jmpf', 0), b'\x66': ('jmpf', 1), b'\xa6': ('jmpf', 2), b'\xe6': ('jmpf', 4),     # if A == 0, jmp
    b'\x27': ('jmpt', 0), b'\x67': ('jmpt', 1), b'\xa7': ('jmpt', 2),                           # if A != 0, jmp
    b'\x28': ('jmp', 0), b'\x68': ('jmp', 1), b'\xa8': ('jmp', 2), b'\xe8': ('jmp', 4),
    
    b'\x29': ('call', 0), b'\x69': ('call', 1), b'\xa9': ('call', 2), b'\xe9': ('call', 4),
    b'\x2a': ('ret', 0),

    # Function calls
    b'\x2b': ('cuscall', 0), b'\x6b': ('cuscall', 1), b'\xab': ('cuscall', 2),
    b'\x2c': ('cuscall0', 0), b'\x6c': ('cuscall0', 1), b'\xac': ('cuscall0', 2), b'\xec': ('syscall1', 4),
    b'\x2d': ('cuscall1', 0), b'\x6d': ('cuscall1', 1), b'\xad': ('cuscall1', 2),
    b'\x2e': ('cuscall2', 0), b'\x6e': ('cuscall2', 1),
    b'\x2f': ('cuscall3', 0), b'\x6f': ('cuscall3', 1),

    b'\x30': ('exit', 0),

    # unused in retail
    b'\x31': ('printnum', 1),
    b'\x32': ('printstr', 0),

    b'\x33': ('push', 0), # push 1, before with 15

    # pop A
    # pop B
    # jmp* location_xxx 
    b'\x34': ('jmpne', 0), b'\x74': ('jmpne', 1), b'\xb4': ('jmpne', 2),    # pop B,pop A, if A != B, jmp
    b'\x35': ('jmpe', 0), b'\x75': ('jmpe', 1), b'\xb5': ('jmpe', 2),       # pop B,pop A, if A == B, jmp

    # pop A
    # pop B
    # &A = B 
    b'\x36': ('store', 0),

}

func_arg_types = {
    b'\x01': 'int',
    b'\x02': 'float',
    b'\x03': 'string',
}


call_func_types = {
    '1': 'Pop()',
    '2': 'void RegisterEvent(function_name, ?, multiple_functions_per_event(?));',
    '12': "WaitOnLoad(",
    '13': 'LoadResource(',
    "14": "LoadMap(",
    '21': 'GetDifficulty(',

    '44': 'void SoundController::PlayBgm(soundname);',
    "100": "SetMap(",
    "105": "MapObjectDestroy4(",
    '140': 'Factor_AllEnemyDestroy(',
    '200': 'Wait(',
    '300': 'PlayBGM(',
    '1050': 'int loc_1401154BF(int, int);',

    '1000': 'CreatePlayer(waypoint, 0);',
    '1001': 'CreatePlayer(waypoint, 1);',
    '1002': 'CreatePlayer(waypoint, 2);',
    '1003': 'int loc_1401170F6(void)    Returns the number of local (?) players.',
    '1005': 'int loc_140117223(int);',
    '1006': 'void loc_140117304(int, int, int);',
    '1007': 'void loc_1401173CB(int, int);',
    '1010': 'int CreateFriend(float, wchar_t*, wchar_t*, bool);',
    '1011': 'int CreateFriendSquad(wchar_t*, float, wchar_t*, wchar_t*, int, float, bool);',
    '1012': 'void loc_1401174E5(wchar_t*, float, wchar_t*, int, float, bool);',
    '1013': 'void loc_140117538(int, wchar_t*, float, wchar_t*, int, float);',
    '1020': 'void CreatNeutral(wchar_t*, wchar_t*, float);',

    '2002': 'void CreateEnemyGroup(waypoint, radius, sgo_name, count, health_scale, has_aggro);',
    '2030': 'CreateEnemySquad(',

    '3100': 'SetAiRouteSpeed(',
    '3101': 'SetAiRoute(',

    '9000': 'CreateEventFactorWait(',
    '9001': 'CreateEventFactorTimer(',
    '9002': 'CreateEventFactorWait2(',

    '9050' : "CreateEventFactorCheckFlagTrue(",
    '9051' : "CreateEventFactorCheckFlagFalse(",
    
    '9100': 'CreateEventFactorAllEnemyDestroy',

    "9110": "CreateEventFactorTeamObjectCount(",
    "9114": "CreateEventFactorTeamGeneratorObjectCount(",

    '9201' : "CreateEventFactorObjectDestroy(",

    '9300': 'CreateEventFactorAiMoveEnd(',
    
    '9400' : "CreateEventPlayerAreaCheck(",
}

# compiler
func_arg_type_byte = {
    'int': b'\x01',
    'float': b'\x02',
    'string': b'\x03',
}

def compiler_bytecode(opcode:str, compiled_operand:bytes = None):
    no_opr = {
        # 0
        'pop': b'\x02',
        'pushtop': b'\x03',
        # 0,
        'sar': b'\x0c',
        'sll': b'\x0d',
        'and': b'\x0e',
        'or': b'\x0f',
        'xor': b'\x10',
        'not': b'\x11',
        'ftoi': b'\x12',
        'itof': b'\x13',
        # 0,
        'ret': b'\x2a',
        # 0,
        'exit': b'\x30',
        # 0,
        'store': b'\x36',
    }
    fixed_opr = {
        # 1
        'cvtstore': b'\x01',
        # 1
        'add': b'\x04',
        'sub': b'\x05',
        'mult': b'\x06',
        'div': b'\x07',
        'mod': b'\x08',
        'neg': b'\x09',
        'inc': b'\x0a',
        'dec': b'\x0b',
        # 1,
        'testnand': b'\x1d',
        'testor': b'\x1e',
        'testz': b'\x1f',
        'testg': b'\x20',
        'testge': b'\x21',
        'teste': b'\x22',
        'testne': b'\x23',
        'testle': b'\x24',
        'testl': b'\x25',
    }
    dynamic_opr = {
        # dynamic
        'loadabs': 0x14,
        'push': 0x15,
        'storeabs': 0x16,
        'loadrel': 0x17,
        'pushrel': 0x18,
        'storerel': 0x19,
        'pushstr': 0x1a,
        'addrel': 0x1b,
        'subrel': 0x1c,
        # dynamic,
        'jmpf': 0x26,
        'jmpt': 0x27,
        'jmp': 0x28,
        'call': 0x29,
        # dynamic,
        'cuscall': 0x2b,
        'cuscall0': 0x2c,
        'cuscall1': 0x2d,
        'cuscall2': 0x2e,
        'cuscall3': 0x2f,
        # dynamic,
        'jmpne': 0x34,
        'jmpe': 0x35,
    }

    if opcode in no_opr:
        compiled_bytecode = no_opr.get(opcode)
    elif opcode in fixed_opr and compiled_operand is not None:
        compiled_bytecode = fixed_opr.get(opcode)
    elif opcode in dynamic_opr and compiled_operand is not None:
        opr_len = len(compiled_operand)
        if opr_len == 1:
            _x = 0x40
        elif opr_len == 2:
            _x = 0x80
        elif opr_len == 4:
            _x = 0xC0
        else:
            _x = 0
        new_bytecode = dynamic_opr.get(opcode) | _x
        compiled_bytecode = new_bytecode.to_bytes(1, byteorder='little')
    else:
        return b''
    if compiled_operand:
        return compiled_bytecode + compiled_operand
    else:
        return compiled_bytecode