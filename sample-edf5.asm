//  全局变量名字定义
name g_sergent    // 0
name g_sergent_follower1    // 1
name g_sergent_follower2    // 2
name g_sergent_follower3    // 3

Mission::Mission:   // 全局变量的初始化
  push  0
  storeabs  0    // g_sergent
  push  1
  neg  0x00
  storeabs  1    // g_sergent_follower1
  push  1
  neg  0x00
  storeabs  2    // g_sergent_follower2
  push  1
  neg  0x00
  storeabs  3    // g_sergent_follower3
  exit

//  无需关心的代码块与代码跳转点, 通常为某作固定样式, 此块为edf5专有
location_0 :
  loadrel     0x00
  addrel      0x03
  ret

location_4 :
  subrel      0x03
  storerel    0x00
  storerel    0x02
  storerel    0x01
  loadrel     0x01
  cuscall0    4000
  cuscall0    4002
  loadrel     0x02
  cuscall0    200    // Wait(
  jmp         location_0

location_25 :
  loadrel     0x00
  addrel      0x01
  ret

location_29 :
  subrel      0x01
  storerel    0x00
  pushstr     "MusenBegin"
  cuscall0    4000
  jmp         location_25

location_38 :
  loadrel     0x00
  addrel      0x01
  ret

location_42 :
  subrel      0x01
  storerel    0x00
  pushstr     "MusenEnd"
  cuscall0    4000
  jmp         location_38

location_52 :
  loadrel     0x00
  addrel      0x03
  ret

location_56 :
  subrel      0x03
  storerel    0x00
  storerel    0x02
  storerel    0x01
  cuscall0    4002
  loadrel     0x02
  cuscall0    200    // Wait(
  call        location_29
  loadrel     0x01
  cuscall0    4000
  call        location_42
  cuscall0    4002
  jmp         location_52

location_84 :
  loadrel     0x00
  addrel      0x02
  ret

location_88 :
  subrel      0x02
  storerel    0x00
  storerel    0x01
  loadrel     0x01
  cuscall0    17
  jmp         location_84

location_103 :
  subrel      0x02
  storerel    0x00
  storerel    0x01

location_122 :
  loadrel     0x00
  addrel      0x01
  ret

location_126 :
  subrel      0x01
  storerel    0x00
  cuscall0    5
  jmp         location_122

location_133 :
  loadrel     0x00
  addrel      0x04
  ret

location_137 :
  subrel      0x04
  storerel    0x00
  storerel    0x01
  cuscall1    10000
  jmpf        location_150
  cuscall0    10003

location_150 :
  pushrel     0x02
  pushstr     "app:/ui/lyt_HUiMissionCleared.sgo"
  cuscall0    39
  store
  loadrel     0x01
  cuscall0    200    // Wait(
  pushrel     0x03
  pushstr     "ui_fade_screen_simple"
  cuscall0    30
  store
  loadrel     0x03
  push        3
  push        3.0f
  cuscall0    50
  loadrel     0x03
  cuscall0    51
  loadrel     0x02
  cuscall0    31
  loadrel     0x03
  cuscall0    31
  push        1
  cuscall0    3
  jmp         location_133

location_196 :
  loadrel     0x00
  addrel      0x01
  ret

location_200 :
  subrel      0x01
  storerel    0x00
  push        2.0f
  cuscall0    301
  push        1.5f
  cuscall0    200    // Wait(
  push        0
  cuscall0    52
  pushstr     "Jingle_MissionCleared"
  cuscall0    300    // PlayBGM(
  push        6.0f
  call        location_137
  jmp         location_196

location_235 :
  loadrel     0x00
  addrel      0x01
  ret

location_239 :
  subrel      0x01
  storerel    0x00
  push        2.0f
  cuscall0    301
  push        1.5f
  cuscall0    200    // Wait(
  push        0
  cuscall0    52
  pushstr     "Jingle_MissionClearedFinal"
  cuscall0    300    // PlayBGM(
  push        10.0f
  call        location_137
  jmp         location_235

location_275 :
  loadrel     0x00
  addrel      0x01
  ret

location_279 :
  subrel      0x01
  storerel    0x00
  push        2.0f
  cuscall0    301
  push        1.5f
  cuscall0    200    // Wait(
  push        0
  cuscall0    52
  pushstr     "Jingle_MissionEscape"
  cuscall0    300    // PlayBGM(
  push        7.0f
  call        location_137
  jmp         location_275

location_315 :
  loadrel     0x00
  addrel      0x06
  ret

location_319 :
  subrel      0x06
  storerel    0x00
  push        0
  storerel    0x03
  push        2
  cuscall1    1    // Pop()
  push        0
  jmpne       location_334
  jmp         location_315

location_334 :
  cuscall0    10001
  push        3.0f
  cuscall0    200    // Wait(
  push        0
  cuscall0    52
  push        2.0f
  cuscall0    301
  push        1.5f
  cuscall0    200    // Wait(
  cuscall1    10000
  jmpf        location_370
  cuscall0    10003

location_370 :
  pushrel     0x02
  pushstr     "app:/ui/lyt_HUiMissionFailed.sgo"
  cuscall0    39
  store
  pushstr     "Jingle_MissionFailed"
  cuscall0    300    // PlayBGM(
  push        5.0f
  cuscall0    200    // Wait(
  cuscall0    10002
  cuscall1    10000
  jmpf        location_402
  cuscall0    10003

location_402 :
  pushstr     "app:/ui/lyt_HUiFailedResult.sgo"
  cuscall0    39
  storerel    0x05
  loadrel     0x05
  cuscall0    33
  pushrel     0x03
  pushstr     ""
  pushstr     ""
  push        0
  cuscall0    38
  store
  pushrel     0x04
  pushstr     "ui_fade_screen_simple"
  cuscall0    30
  store
  loadrel     0x04
  push        3
  push        0.5f
  cuscall0    50
  loadrel     0x04
  cuscall0    51
  loadrel     0x02
  cuscall0    31
  loadrel     0x04
  cuscall0    31
  loadrel     0x03
  push        1
  jmpne       location_467
  push        3
  cuscall0    3
  jmp         location_315

location_467 :
  loadrel     0x03
  push        2
  jmpne       location_315
  push        2
  cuscall0    3
  jmp         location_315

location_481 :
  loadrel     0x00
  addrel      0x05
  ret

location_485 :
  subrel      0x05
  storerel    0x00
  storerel    0x04
  storerel    0x03
  storerel    0x02
  storerel    0x01
  push        10.0f
  push        0.10000000149011612f
  push        0.05000000074505806f
  loadrel     0x02
  loadrel     0x01
  push        0.5f
  push        0.5f
  push        0.5f
  push        2.0f
  push        2.0f
  push        2.0f
  push        100.0f
  loadrel     0x03
  push        40.0f
  loadrel     0x04
  cuscall0    5100
  jmp         location_481

location_564 :
  loadrel     0x00
  addrel      0x07
  ret

location_568 :
  subrel      0x07
  storerel    0x00
  storerel    0x06
  storerel    0x05
  storerel    0x04
  storerel    0x03
  storerel    0x02
  storerel    0x01
  loadrel     0x01
  loadrel     0x02
  push        0.5f
  loadrel     0x03
  push        1.0f
  push        2.0f
  push        2.0f
  push        2.0f
  push        200.0f
  loadrel     0x04
  push        40.0f
  loadrel     0x05
  loadrel     0x06
  cuscall0    5101
  jmp         location_564

location_635 :
  loadrel     0x00
  addrel      0x08
  ret

location_639 :
  subrel      0x08
  storerel    0x00
  storerel    0x07
  storerel    0x06
  storerel    0x05
  storerel    0x04
  storerel    0x03
  storerel    0x02
  storerel    0x01
  loadrel     0x01
  loadrel     0x02
  push        0.5f
  loadrel     0x03
  loadrel     0x04
  push        2.0f
  push        2.0f
  push        2.0f
  push        200.0f
  loadrel     0x05
  push        40.0f
  loadrel     0x06
  loadrel     0x07
  cuscall0    5101
  jmp         location_635

location_705 :
  loadrel     0x00
  addrel      0x07
  ret

location_709 :
  subrel      0x07
  storerel    0x00
  storerel    0x06
  storerel    0x05
  storerel    0x04
  storerel    0x03
  storerel    0x02
  storerel    0x01
  loadrel     0x01
  loadrel     0x02
  push        10.0f
  loadrel     0x03
  loadrel     0x04
  loadrel     0x05
  loadrel     0x06
  cuscall0    5102
  jmp         location_705

location_746 :
  loadrel     0x00
  addrel      0x07
  ret

location_750 :
  subrel      0x07
  storerel    0x00
  storerel    0x06
  storerel    0x05
  storerel    0x04
  storerel    0x03
  storerel    0x02
  storerel    0x01
  loadrel     0x01
  loadrel     0x02
  push        10.0f
  loadrel     0x03
  loadrel     0x04
  loadrel     0x05
  loadrel     0x06
  cuscall0    5103
  jmp         location_746


location_mainret:   // main函数的call调用返回块部分 
  loadrel     0x00
  addrel      0x02
  ret

location_masin:     // 主脚本核心
  subrel      0x02
  storerel    0x00
  push        0
  push        0
  push        0
  push        0
  cuscall0    18
  push        0
  call        location_88   // EconomyMode
  call        location_126  // InitializeCommon
  cuscall0    10
  //    预读取不可变资源
  pushstr     "app:/ui/lyt_HUiMissionCleared.sgo"
  push        -1
  cuscall0    13    // LoadResource(
  pushstr     "app:/ui/lyt_HUiMissionFailed.sgo"
  push        -1
  cuscall0    13    // LoadResource(
  pushstr     "app:/ui/lyt_HUiFailedResult.sgo"
  push        -1
  cuscall0    13    // LoadResource(
    //    预读取地图
  pushstr     "app:/Map/NW_Henden.mac"
  pushstr     "fine"
  push        -1
  cuscall0    14    // LoadMap(
      // 预读取物体sgo
  pushstr     "app:/object/GIANTSPIDER01.SGO"
  push        -1
  cuscall0    13    // LoadResource(
      // ------------
  cuscall0    16
  cuscall0    12    // WaitOnLoad(
  cuscall0    10000
  cuscall0    11
  //  设置地图调用块
  pushstr     "app:/Map/NW_Henden.mac"
  pushstr     "fine"
  cuscall0    100    // SetMap(
      //  创建玩家实体
  pushstr     "プレイヤー"
  cuscall0    1000    // CreatePlayer(waypoint, 0);
  //  播放bgm
  pushstr     "BGM_inGame_Soutousen"
  cuscall0    300    // PlayBGM(
      //  将实体放入地图种
  pushstr     "プレイヤー"
  push        0.0f
  pushstr     "app:/object/GIANTSPIDER01.SGO"
  push        10
  push        0.1f
  push        0
  cuscall0    2002    // void CreateEnemyGroup(waypoint, radius, sgo_name, count, health_scale, has_aggro);
    // 下一个命名函数跳转, 绑定事件
  pushstr     "Func_1"
  push        110.0f
  push        0
  cuscall0    2    // void RegisterEvent(function_name, ?, multiple_functions_per_event(?));
    // 注册事件
  push        10.0f
  cuscall0    9100    // CreateEventFactorAllEnemyDestroy
  //  无条件跳转
  jmp location_mainret

    // 有名函数call调用返回块部分
location_func1ret :
  loadrel     0x00
  addrel      0x01
  ret
    // 有名函数核心
location_func1in:
  subrel      0x01
  storerel    0x00
  loadabs     0    // Func_1___Counter
  pushtop
  inc         0x00
  storeabs    0    // Func_1___Counter
  pop
  push        1
  loadabs     0    // Func_1___Counter
  push        1
  testne      0x00
  testnand    0x00
  jmpf        location_905
  jmp         location_func1ret


location_905 :
  push        1.0f
  cuscall0    9
  push        1
  cuscall1    1    // Pop()
  push        0
  jmpne       location_920
  jmp         location_881ret

location_920 :
  call        location_200  //  MissionClear  胜利
  jmp         location_881ret

 //  无需关心的代码块与代码跳转点, 通常为某作固定样式, 此块为edf5专有
Voice2:   /- (string, float)
  call        location_4
  exit

RadioBegin:   /- ()
  call        location_29
  exit

RadioEnd:   /- ()
  call        location_42
  exit

RadioVoice:   /- (string, float)
  call        location_56
  exit

EconomyMode:   /- (int)
  call        location_88
  exit

WaitAiMoveEnd:   /- (int)
  call        location_103
  exit

InitializeCommon:   /- ()
  call        location_126
  exit

MissionClear_Common:   /- (float)
  call        location_137
  exit

MissionClear:   /- ()
  call        location_200
  exit

FinalMissionClear:   /- ()
  call        location_239
  exit

MissionEscapeClear:   /- ()
  call        location_279
  exit

MissionGameOverEvent:   /- ()
  call        location_319
  exit

SceneEffect_Snow:   /- (float, float, int, float)
  call        location_485
  exit

SceneEffect_Rain:   /- (float, float, float, int, float, float)
  call        location_568
  exit

SceneEffect_RainEx:   /- (float, float, float, float, int, float, float)
  call        location_639
  exit

SceneEffect_FugitiveDust:   /- (float, int, float, float, float, float)
  call        location_709
  exit

SceneEffect_Fog:   /- (float, int, float, float, float, float)
  call        location_750
  exit

    // 主函数入口
Mission::Main:
  call location_masin
  exit
    // 有名函数入口
Mission::Func_1:
  call location_func1in
  exit