
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

'''
|-----|
|  A  |
|  B  |

** 在该代码里,
push A
push B
testg  // (A < B)
jmpt   // if (A < B) == True
jmpf   // if (A < B) == False
'''
asm_opcode = {
    # pop B
    # pop A
    # *A = B
    # push B 
    b'\x01': ('cvtstore', 1),

    b'\x02': ('pop', 0),
    b'\x03': ('pushtop', 0),

    # pop B
    # pop A
    # ***
    b'\x04': ('add', 1),    # push (A + B)
    b'\x05': ('sub', 1),    # push (A - B)
    b'\x06': ('mult', 1),   # push (A * B)
    b'\x07': ('div', 1),    # push (A / B)
    # pop B
    # pop A
    # mod 
    b'\x08': ('mod', 1),    # push (A % B)

    # stack first variable
    b'\x09': ('neg', 1),    # 1 -> -1 or -1 -> 1
    b'\x0a': ('inc', 1),    # ++
    b'\x0b': ('dec', 1),    # --

    # pop B
    # pop A
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
    b'\x24': ('testle', 1),     # if A >= B  (push 1) else (push 0)
    b'\x25': ('testl', 1),      # if A > B (push 1) else (push 0)

    # jump
    # pop A
    # jmp* location_xxx 
    b'\x26': ('jmpf', 0), b'\x66': ('jmpf', 1), b'\xa6': ('jmpf', 2), b'\xe6': ('jmpf', 4),     # if A == 0, jmp
    b'\x27': ('jmpt', 0), b'\x67': ('jmpt', 1), b'\xa7': ('jmpt', 2),                           # if A != 0, jmp
    b'\x28': ('jmp', 0), b'\x68': ('jmp', 1), b'\xa8': ('jmp', 2), b'\xe8': ('jmp', 4),
    
    b'\x29': ('call', 0), b'\x69': ('call', 1), b'\xa9': ('call', 2), b'\xe9': ('call', 4),
    b'\x2a': ('ret', 0),

    # Function calls
    b'\x2b': ('cuscall', 0), b'\x6b': ('cuscall', 1), b'\xab': ('cuscall', 2), b'\xeb': ('cuscall', 4),
    b'\x2c': ('cuscall0', 0), b'\x6c': ('cuscall0', 1), b'\xac': ('cuscall0', 2), b'\xec': ('cuscall0', 4),
    b'\x2d': ('cuscall1', 0), b'\x6d': ('cuscall1', 1), b'\xad': ('cuscall1', 2), b'\xed': ('cuscall1', 4),
    b'\x2e': ('cuscall2', 0), b'\x6e': ('cuscall2', 1), b'\xae': ('cuscall2', 2), b'\xee': ('cuscall2', 4),
    b'\x2f': ('cuscall3', 0), b'\x6f': ('cuscall3', 1), b'\xaf': ('cuscall3', 2), b'\xef': ('cuscall3', 4),

    b'\x30': ('exit', 0),

    # unused in retail
    b'\x31': ('printnum', 1),
    b'\x32': ('printstr', 0),

    b'\x33': ('push', 0), # push 1, before with 15

    # pop B
    # pop A
    # jmp* location_xxx 
    b'\x34': ('jmpne', 0), b'\x74': ('jmpne', 1), b'\xb4': ('jmpne', 2),    # pop B,pop A, if A != B, jmp
    b'\x35': ('jmpe', 0), b'\x75': ('jmpe', 1), b'\xb5': ('jmpe', 2),       # pop B,pop A, if A == B, jmp

    # pop B
    # pop A
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
    '12': "CheckResourcesLoaded()",
    '13': 'LoadResource(string resource, int)',
    "14": "LoadMapResource(string map, string weather, int)",
    '18': 'pops four elements',
    '21': 'int GetDifficulty()',

    '30': 'int CreateUiElement(string Element)',
    '31': 'DestroyUiElement(int id)',
    '39': 'int CreateLytUiElement(sgo)',

    '44': 'void SoundController::PlayBgm(soundname);',
    '45': 'FadeOutBGM(timeDelta);',
    '46': 'FadeInBGM(soundname, timeDelta);',
    '50': 'FadeUiElement?(int id, int fadeType, float time)',
    '51': 'WaitForUiFade(int id)',
    '66': 'VsStartPosition(SpawnPrefix)',
    '80': 'RecruitObject(int leader, int follower)',
    '95': 'PlaySurroundSE(spawnpoint, SoundPreset)',
    "100": "SetMap(",
    "102": "MapObjectDestroy(shapeNode)",
    "103": "MapObjectDestroy2(shapeNode)",
    "104": "MapObjectDestroy3(shapeNode)",
    "105": "MapObjectDestroy4(shapeNode)",
    "110": "MapObjectInvincible(shapeNode)",
    "128": "SetObjectAction(int id, int action)",
    '132': 'AddToMobGroup(string sgo, float)',
    '134': 'CreateMobPath(routeNode, amount, spawndelay, lifeTime)',
    '140': 'Factor_AllEnemyDestroy(',
    '200': 'Wait(float)',
    '209': 'MultiplyObjectHealth(int id, float percent)',
    '210': 'SetEssential(int id, bool Essential)',
    '213': 'SetObjectPosition(int, string)',
    '234': 'SetObjectEnemy(int id)',
    '235': 'SetObjectNeutral(int id)',
    '236': 'SetObjectTeam(int id, int team)',
    '254': 'int CreateTransporter(str, str, str, str, str,float)',
    '255': 'int CreateTransporter2(str, str, str, str, str,float)',
    '257': 'int CreateEventObject(spawnpoint, sgo)',
    '258': 'int CreateEventObject2(spawnpoint, sgo)',
    '261': 'int CreateVehicle2(spawnpoint, sgo, scale)',
    '287': 'ObjectNotOnRoute(int id)',
    '288': 'CreateExplosion(spawnpoint, SizeDuration, quakeScale)',
    '289': 'CreateQuake(spawnpoint, SizeDuration, quakeScale)',
    '300': 'PlayBGM(',
    '308': 'SetGenerator(int id, int, sgo, int amount,float scale, float rate, float interval, bool)',
    '350': 'PlayPresetSE(str SoundPreset)',
    '356': 'SetAiObjectDirectionPoint(int, str, float, bool)',
    '421': 'LookCameraToArea(sphereShape, time)',

    '1000': 'CreatePlayer(waypoint);',
    '1001': 'CreatePlayer2(waypoint);  will crash',
    '1002': 'CreatePlayer3(waypoint);  will crash',
    '1003': 'int GetPlayerCount(void) ',
    '1005': 'int loc_140117223(int);',
    '1006': 'void loc_140117304(int, int, int);',
    '1007': 'void loc_1401173CB(int, int);',
    '1010': 'int CreateFriend(spawnpoint, sgo, scale, canRecruit);',
    '1011': 'int CreateFriendSquad(str spawnpoint, float radius, str sgo_leader, str sgo_follower, int count, float hpScale, bool canRecruit);',
    '1012': 'void CreateFriendGroup(str spawnpoint, float radius, str sgo, int count, float scale, bool canRecruit);',
    '1013': 'void loc_140117538(int, wchar_t*, float, wchar_t*, int, float);',
    '1020': 'int CreatNeutral(spawnpoint, sgo, scale);',
    '1021': 'int create_Vehicle(spawnpoint, sgo)',
    '1050': 'int loc_1401154BF(int, int);',

    '2000': 'int CreateEnemy(spawnpoint, sgo, scale, active)',
    '2001': 'int CreateEnemy2(spawnpoint, sgo, scale, active)',
    '2002': 'void CreateEnemyGroup(waypoint, radius, sgo_name, count, health_scale, has_aggro);',
    '2003': 'void CreateEnemyGroup2(waypoint, radius, sgo_name, count, health_scale, has_aggro);',
    '2004': 'create_enemy_spawn_ground(spawnpoint, radius, sgo, count, scale, active, time)',
    '2005': 'CreateEnemyGroupGround2(spawnpoint, radius, sgo, count, scale, active, time)',
    '2006': 'CreateFlyingEnemyGroup_Area(shapeNode, sgo, count, scale, active)',
    '2007': 'CreateFlyingEnemyGroup_AreaRoute(shapeNode, routeNode, sgo, count, scale, active)',
    '2008': 'CreateFlyingEnemyGroup_Area2(shapeNode, sgo, count, scale, active)',
    '2009': 'CreateEnemyGroupGround_Area(shapeNode, sgo, count, scale, active)',
    '2010': 'CreateFlyingEnemyGroup_AreaRoute2(ShapeNode, routeNode, sgo, count, hpScale, active)',
    '2011': 'int CreateEnemySpawn(spawnpoint, sgoName, hpScale, active)',
    '2022': 'CreateFlyingEnemyGroup_OnRoute(str routeNode, flaot distance, str sgoName, int count, float hpScale, bool active)',
    '2023': 'int CreateEnemy3(string spawnpoint, string sgo_name, float hpScale, bool active)',
    '2030': 'int CreateEnemySquad(spawnpoint, radius, sgo_leader, scale_leader, sgo_follower, count, scale_follower, active)',

    '2100': 'set_generator?',
    '2101': 'set_generator_once?',
    '3020': 'set_no_damage_time(float)?',
    '3100': 'SetAiRouteSpeed(int id, float speedfactor)',
    '3101': 'SetAiRoute(int ID, string path)',
    '3102': 'SetAiPath(int ID, string Path)',
    '3103': 'NotOnPath?',

    '3200': 'set_object_stage?',
    '3202': 'object_destroy?(int id)',

    '4006': 'SetChatter(int id, bool CanTalk)',


    # float Depth1, 
    # float Depth2, 
    # float EdgeRadius, 
    # float DecalVeritality,
    # float Progress,
    # float DecalRed,
    # float DecalGreen,
    # float DecalBlue,
    # float SpecularRed,
    # float SpecularGreen,
    # float SpecularBlue,
    # float SpecularSize,
    # int ParticleAmount,
    # float ParticleDistance,
    # float ParticleSpeed,
    '5100': 'SetEffectSnow(**)',
    '5101': 'SetEffectRain(**)',
    '5102': 'SetEffectDust(**)',
    '5102': 'SetEffectFog(**)',

    '9000': 'CreateEventFactorWait(float TimeDelta)',
    '9001': 'CreateEventFactorTimer(int, float, TimeDelta)',
    '9002': 'CreateEventFactorWait2(float TimeDelta)',

    '9044': 'CreateEventFactorAiMoveEnd(int ID)',
    '9045': 'CreateEventFactorAiMoveEndOrDie(int ID)',

    '9050': "CreateEventFactorCheckFlagTrue(int)",
    '9051': "CreateEventFactorCheckFlagFalse(int)",
    '9054': 'CreateEventFactorAiFollow(int Soldier)',

    '9100': 'CreateEventFactorAllEnemyDestroy(float delay)',

    "9110": "CreateEventFactorTeamObjectCount(int team, int count)",
    '9111': 'createEventFactor_mothershipShieldCount?',
    "9112": "CreateEventFactorAreaTeamObjectCount(string ShapeNode, int team, int count)",
    "9113": "CreateEventFactorTeamBigObjectCount(int team, int count)",
    "9114": "CreateEventFactorTeamGeneratorObjectCount(int count)",
    "9116": "CreateEventFactorObjectGroupCount(int, int)",
    "9117": "CreateEventFactorObjectGroupEncount(int)",
    "9120": "CreateEventFactorTeamEncount(int team)",
    "9121": "CreateEventFactorTeamNotEncount(int team)",
    "9144": "CreateEventFactorPlayerAreaCheck(string ShapeNode)",

    '9201': "CreateEventFactorObjectDestroy(id)",
    '9202': "CreateEventFactorObjectDelete(id)",

    '9300': 'CreateEventFactorAiMoveEnd(',
    
    '9400': "CreateEventPlayerAreaCheck(",
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