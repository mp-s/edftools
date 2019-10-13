name g_sergent    // 0
name g_sergent_follower1    // 1
name g_sergent_follower2    // 2
name g_sergent_follower3    // 3

Mission::Mission:
  push  1
  neg  0x00
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

Mission::Main:
  call        location_791
location_791 :
  subrel      0x02
  storerel    0x00
  push        0
  push        0
  push        0
  push        0
  cuscall0    18
  push        0
  call        location_88
  call        location_126
  cuscall0    10
  pushstr     "app:/ui/lyt_HUiMissionCleared.sgo"
  push        -1
  cuscall0    13    // LoadResource(
  pushstr     "app:/ui/lyt_HUiMissionFailed.sgo"
  push        -1
  cuscall0    13    // LoadResource(
  pushstr     "app:/ui/lyt_HUiFailedResult.sgo"
  push        -1
  cuscall0    13    // LoadResource(
  pushstr     "app:/Map/nw_Hillycity_light.mac"
  pushstr     "fine"
  push        -1
  cuscall0    14    // LoadMap(
  cuscall0    16
  cuscall0    12    // WaitOnLoad(
  cuscall0    10000
  cuscall0    11
  pushstr     "app:/Map/nw_Hillycity_light.mac"
  pushstr     "fine"
  cuscall0    100    // SetMap(
  pushstr     "プレイヤー"
  cuscall0    1000    // CreatePlayer(waypoint, 0);
  jmp         location_787
location_787 :
  loadrel     0x00
  addrel      0x02
  ret
  exit

Voice2:   /- (string, float)
  call        location_4
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
location_0 :
  loadrel     0x00
  addrel      0x03
  ret
  exit

RadioBegin:   /- ()
  call        location_29
  exit

RadioEnd:   /- ()
  call        location_42
  exit


location_29 :
  subrel      0x01
  storerel    0x00
  pushstr     "MusenBegin"
  cuscall0    4000
  jmp         location_25

location_42 :
  subrel      0x01
  storerel    0x00
  pushstr     "MusenEnd"
  cuscall0    4000
  jmp         location_38

RadioVoice:   /- (string, float)
  call        location_56
  exit

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
location_52 :
  loadrel     0x00
  addrel      0x03
  ret

EconomyMode:   /- (int)
  call        location_88
  exit

location_88 :
  subrel      0x02
  storerel    0x00
  storerel    0x01
  loadrel     0x01
  cuscall0    17
  jmp         location_84
location_84 :
  loadrel     0x00
  addrel      0x02
  ret

WaitAiMoveEnd:   /- (int)
  call        location_103
location_103 :
  subrel      0x02
  storerel    0x00
  storerel    0x01
  exit

InitializeCommon:   /- ()
  call        location_126
  exit
location_126 :
  subrel      0x01
  storerel    0x00
  cuscall0    5
  jmp         location_122

location_122 :
  loadrel     0x00
  addrel      0x01
  ret

MissionClear_Common:   /- (float)
  call        location_137
  exit

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

location_133 :
  loadrel     0x00
  addrel      0x04
  ret

MissionClear:   /- ()
  call        location_200
  exit
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

location_196 :
  loadrel     0x00
  addrel      0x01
  ret

FinalMissionClear:   /- ()
  call        location_239
  exit
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

location_235 :
  loadrel     0x00
  addrel      0x01
  ret

MissionEscapeClear:   /- ()
  call        location_279
  exit
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

location_275 :
  loadrel     0x00
  addrel      0x01
  ret

MissionGameOverEvent:   /- ()
  call        location_319
  exit

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

location_315 :
  loadrel     0x00
  addrel      0x06
  ret

SceneEffect_Snow:   /- (float, float, int, float)
  call        location_485
  exit

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

location_481 :
  loadrel     0x00
  addrel      0x05
  ret

SceneEffect_Rain:   /- (float, float, float, int, float, float)
  call        location_568
  exit
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

location_564 :
  loadrel     0x00
  addrel      0x07
  ret


SceneEffect_RainEx:   /- (float, float, float, float, int, float, float)
  call        location_639
  exit

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
location_635 :
  loadrel     0x00
  addrel      0x08
  ret

SceneEffect_FugitiveDust:   /- (float, int, float, float, float, float)
  call        location_709
  exit
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
location_705 :
  loadrel     0x00
  addrel      0x07
  ret

SceneEffect_Fog:   /- (float, int, float, float, float, float)
  call        location_750
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
location_746 :
  loadrel     0x00
  addrel      0x07
  ret

  exit

