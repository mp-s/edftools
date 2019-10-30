
+ preload map
```cs
  pushstr     "app:/Map/NW_Henden.mac"
  pushstr     "fine"
  push        -1
  cuscall0    14    // LoadMap(
```

- preload object
```py
  pushstr     "app:/object/GIANTSPIDER01.SGO"
  push        -1
  cuscall0    13    // LoadResource(
```

+ setup map
```js
  pushstr     "app:/Map/NW_Henden.mac"
  pushstr     "fine"
  cuscall0    100    // SetMap(
```

+ create player
```c
  pushstr     "プレイヤー"
  cuscall0    1000    // CreatePlayer(waypoint);
```

- create enemies
```java
  pushstr     "プレイヤー"
  push        0.0f
  pushstr     "app:/object/GIANTSPIDER01.SGO"
  push        10
  push        0.1f
  push        0
  cuscall0    2002    // void CreateEnemyGroup(waypoint, radius, sgo_name, count, health_scale, has_aggro);
```

- register event
```json
  push        110.0f
  push        0
  cuscall0    2    // void RegisterEvent(function_name, ?, multiple_functions_per_event(?));
```

- all enemy destroy factor
```cpp
  push        10.0f
  cuscall0    9100    // CreateEventFactorAllEnemyDestroy(float delay)
```

- game difficulty
```c
if (getDifficulty() < 3)
{
    locaiton_1130
}
```  
```c
  cuscall0    21    // GetDifficulty(
  push        3
  testg       0x00  // A < B ?
  jmpf        location_1130
```

- creat friend npc1
```? g_sergent = CreateFriend(float, str, str, int) ?```  
```c
  push        41    // g_sergent
  pushstr     "小隊01"
  pushstr     "app:/object/AiArmySoldier_S_AF_Leader.sgo"
  push        0.6000000238418579f
  push        0
  cuscall0    1010    // int CreateFriend(float, wchar_t*, wchar_t*, bool);
  store           // g_sergent = returned int
```

- follower?
```c
  push        42      // g_sergent_follower1
  loadabs     41    // g_sergent
  push        0
  cuscall0    3400
  store             // 
```

- respawn available ?
```c
  loadabs     44    // g_sergent_follower3
  push        1
  cuscall0    3026
```

- create *anchor* ```传送塔  テレポーション・アンカー```  
```c
  push        47    // global var
  pushstr     "ジェネレータ3"
  pushstr     "app:/object/e505_generator.sgo"
  push        1.0f
  push        1
  cuscall0    2001  // int CreateEnemy2(spawnpoint, sgo, scale, active)
  store             // global_var_47 = returned int
```

- generator object
```c
  loadabs     47    // generator2
  push        0
  pushstr     "app:/object/GiantAnt01.sgo"
  push        20
  push        1.0f
  push        0.5f
  push        5.0f
  push        0
  cuscall0    2100    // SetGenerator(int id, int, str sgo, int amount, float hpScale, float rate, float interval, bool)
```

- object move
```c
  loadabs     41    // g_sergent
  pushstr     "小隊移動ルート2"
  cuscall0    3101    // SetAiRoute(int ID, string path)
```

- object route speed
```c
  loadabs     60    // carrier02
  push        0.41999998688697815f
  cuscall0    3100    // SetAiRouteSpeed(int id, float speedfactor)
```