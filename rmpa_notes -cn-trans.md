All offsets are calculated from the first byte of the respective data block (relative offsets).
Route and Camera Waypoints aren't extended to keep aligned to 0, so only the first in a route will always be at 0.

```
    HHHH HHHH 0000 0000 AAAA AAAA aaaa aaaa  
    BBBB BBBB bbbb bbbb CCCC CCCC cccc cccc  
    DDDD DDDD dddd dddd 0000 0000 0000 0000  
```
**RMPA Header**, which is about 0x30 in length:  
+ `H` 0x00 RMP file type string, or PMR because of byte-swapping.
    > 文件头 决定大小端
+ `A` 0x08 boolean denoting if routes are to be processed.
    > 路线?  
    > 是否唯一值, 下一块(0)重复(1)不重复  
+ `a` 0x0C offset to route data.
    > 默认 `0x30`  
+ `B` 0x10 boolean denoting if shapes are to be processed.
    > 形状?  
    > 是否唯一值, 下一块(0)重复(1)不重复  
+ `b` 0x14 offset to shape data.
+ `C` 0x18 boolean denoting if camera paths are to be processed.
    > 相机?  
    > 是否唯一值, 下一块(0)重复(1)不重复   
+ `c` 0x1C offset to camera path data.
+ `D` 0x20 boolean denoting if spawnpoints are to be processed.
    > 刷新点
    > 就目前解析来看, 肯定是 `True`
+ `d` 0x24 offset to spawnpoint data.
    > 刷新点数据块的偏移地址
 When there are less types of data (only spawns for example) the unused offsets will be duplicate pointers.  
    > 当数据类型较少时（例如`仅生成`），未使用的偏移量将是重复的指针。
   
```
    AAAA AAAA BBBB BBBB 0000 0000 CCCC CCCC 
    DDDD DDDD 0000 0000 EEEE EEEE 0000 0000 
```
**Type Headers**, which are exactly 0x20 in length:  
+ `A` 0x00 is how many Enumeration Sub-Headers there are.
    > 多少枚举子头  
+ `B` 0x04 is an offset to the start of the first enumerator?
    > 第一个枚举器的起始偏移?  
+ `C` 0x0C is an offset to the end of the type's data (ends up at the same place as where the next type of data starts).
    > 是类型数据末尾的偏移量  
    >（与下一种数据类型的起始位置相同）。  
+ `D` 0x10 is the numeric waypoint identifier based on the whole RMPA.
    > 是基于整个RMPA的数字航点标识符。
+ `E` 0x18 points to a null string? Or, possibly the string table for some reason?
    > 指向空字符串？ 或者，可能是出于某种原因的字符串表？
  
  
```
    0000 0000 0000 0000 AAAA AAAA 0000 0000 
    bbbb bbbb BBBB BBBB CCCC CCCC DDDD DDDD 
```
**Enumeration Sub-Headers**, which are exactly 0x20 in length:  
> 枚举子头
+ `A` 0x08 points to where the enumeration will end.
    > 指向枚举将结束的位置。 
+ `b` 0x10 字符串长度
+ `B` 0x14 is an offset to a string, possibly just a name.
    > 是字符串的偏移量，可能只是名称。
+ `C` 0x18 is how many pieces of data to process. Multiple Enumeration Sub-Headers add up to the total amount of data pieces in the section.  
    > 是要处理多少数据。 多个枚举子标题加起来等于该部分中数据的总数。
+ `D` 0x1C points to where the enumeration will start.
    > 指向枚举将开始的位置。
  
  
```
    0000 0000 AAAA AAAA BBBB BBBB 0000 0000 
    cccc cccc CCCC CCCC DDDD DDDD EEEE EEEE 
```
**Camera Type Headers**, which are exactly 0x20 in length:
+ `A` 0x04 is an offset to the end of the type's data (ends up at the same place as where the next type of data starts).
    > 类型数据末尾的偏移量（终止于下一个数据类型开始的位置）。
+ `B` 0x08 is the numeric waypoint identifier based on the whole RMPA.
    > 基于整个RMPA的数字航点标识符。
+ `c` 0x10 字符串长度
+ `C` 0x14 points to a null string?
    > 指向空字符串？
+ `D` 0x18 is how many Camera Enumeration Sub-Headers there are?
    > 有多少个照相机枚举子标题？
+ `E` 0x1C is an offset to the start of the first enumerator?
    > 第一个枚举数的起始位置偏移量？
  
```
    0000 0000 AAAA AAAA 0000 0000 0000 0000 
    0000 0000 BBBB BBBB CCCC CCCC DDDD DDDD 
    0000 0000 EEEE EEEE 0000 0000 FFFF FFFF 
```
**Camera Enumeration Sub-Headers**, which are exactly 0x30 in length:
+ `A` 0x04 points to where the enumeration will end.
    > 指向枚举将结束的位置。
+ `B` 0x14 is an offset to a string, possibly just a name.
    > 字符串的偏移量，可能只是名称。
+ `C` 0x18 is how many camera nodes to process.
    > 要处理多少个摄像机节点。
+ `D` 0x1C points to where the enumeration will start.
    > 指向枚举将开始的位置。
+ `E` 0x24 is an offset to a timing enumerator?
    > 定时枚举数的偏移量？
+ `F` 0x2C is an offset to a different timing enumerator?
    > 与其他计时枚举数的偏移量？

Types:
```
    0x00
    AAAA AAAA 0000 0000 BBBB BBBB 0000 0000  0x0F  
    CCCC CCCC 0000 0000 gggg gggg DDDD DDDD  0x1F  
    0000 0000 EEEE EEEE 0000 0000 0000 0000  0x2F  
    0000 0000 FFFF FFFF 0000 0000 
                                  0x3C
```
**Route Waypoints**, which are exactly 0x3C in length:
Remember! All offsets are calculated from the first byte of the _individual waypoint's_ data block.
> 记得！ 所有偏移量都是从“单个航点”的数据块的第一个字节计算得出的。
+ `A` 0x00 is the waypoint's number in the current route, starting from 0.
    > 当前路线中的航点编号，从0开始。
+ `B` 0x08 is an offset to a 0x10 sized block that controls what the next waypoint will be.
    > 一个0x10大小的块的偏移量，该块控制下一个航点的位置。
+ `C` 0x10 is an offset to an SGO that'll apply extra settings, mostly just width.
    > SGO的偏移量，它将应用额外的设置，大部分只是宽度。
+ `g` 0x18 扩展的sgo文件体积
+ `D` 0x1C is another offset to the same SGO? (possibly the real offset that's used?)
    > 同一SGO的另一个offset？ （可能是使用的实际偏移量？）
+ `E` 0x14 is the numeric waypoint identifier based on the whole RMPA.
    > 基于整个RMPA的数字航点标识符。
+ `F` 0x24 is an offset to the path waypoint's name. Not all waypoints direct to a valid string since not all are used by name.
    > 路径航路点名称的偏移量。 并非所有航路点都直接指向有效字符串，因为并非所有航路点都按名称使用。
  
  
```
    0000 0000 0000 0000 AAAA AAAA 0000 0000 
    BBBB BBBB 0000 0000 0000 0000 0000 0000 
    0000 0000 CCCC CCCC 0000 0000 0000 0000 
```
**Shape Setup**, which are about 0x30 in length:
+  `A` 0x08 is the string offset naming the shape type (rectangle, sphere, whatwasthethird).
    > 是命名形状类型（矩形，球形，其他等等）的字符串偏移量。
+  `B` 0x10 is the offset to the shape's name.
    > 形状名称的偏移量。
+  `C` 0x24 is the offset to the shape's size data.
    > 形状尺寸数据的偏移量。

```
    AAAA AAAA BBBB BBBB CCCC CCCC 0000 0000 
    DDDD DDDD EEEE EEEE FFFF FFFF 0000 0000 
    GGGG GGGG 0000 0000 0000 0000 0000 0000 
    0000 0000 0000 0000 0000 0000 0000 0000 
```
**Shape Data**, which are about 0x40 in length:
+ `A` 0x00 position X?
+ `B` 0x04 position Y?
+ `C` 0x08 position Z?
+ `D` 0x10 rectangle size X?
+ `E` 0x14 rectangle size Y?
+ `F` 0x18 rectangle size Z?
+ `G` 0x30 sphere diameter?
    > 球直径？
  

```
    0x00
    0000 0000 0000 0000 0000 0000 AAAA AAAA  0x0F  
    BBBB BBBB CCCC CCCC DDDD DDDD 0000 0000  0x1F  
    0000 0000 0000 0000 0000 0000 0000 0000  0x2F  
    0000 0000 0000 0000 0000 0000 0000 0000  0x3F  
    0000 0000 0000 0000 0000 0000 0000 0000  0x4F  
    0000 0000 0000 0000 0000 0000 0000 0000  0x5F  
    0000 0000 0000 0000 EEEE EEEE 0000 0000  0x6F  
    0000 0000 
              0x74

```
**Camera Path Nodes**, which are exactly 0x74 in length:
Remember! All offsets are calculated from the first byte of the _individual node's_ data block.
> 记得！ 所有偏移量都是从“单个节点”的数据块的第一个字节开始计算的。
+ `A` 0x0C is an offset to an SGO.
    > sgo 内嵌的偏移
+ `B` 0x10 is the numeric waypoint identifier based on the whole RMPA.
    > 基于整个RMPA的数字航点标识符。
+ `C` 0x14 is 3F80 all the time?
    > 全部是 3f80?
+ `D` 0x18 above float 4100 a lot, sometimes zero?
    > 0X18 上面的float 4100很多，有时为零？
+ `E` 0x68 is the offset to the node's name.
    > 节点名称的偏移量。

```
    AAAA AAAA BBBB BBBB CCCC CCCC 0000 0000  
```
**Camera Timing?? Enumerators**, which are about 0x10 in length:
+ `A` 0x00 is a float of some kind, but can be zero.
    > 某种浮点数，但可以为零。
+ `B` 0x04 is how many nodes to process (this and the other timing enum add up to the camera path nodes minus one?).
    > 要处理多少个节点（这个和另一个计时枚举加起来等于相机路径节点减去一个？）。
+ `C` 0x08 is an offset to the start of the nodes.
    > 节点起点的偏移量

```
    AAAA AAAA BBBB BBBB CCCC CCCC 0000 0000 
    0000 0000 DDDD DDDD EEEE EEEE 
```
**Camera Timing?? Nodes**, which are exactly 0x1C in length:
+ `A` 0x00 a float
+ `B` 0x04 a float
+ `C` 0x08 always int 1?
+ `D` 0x14 always float 1?
+ `E` 0x18 always float 1?

```
    0000 0000 AAAA AAAA BBBB BBBB ---- ---- 
    ---- ---- ---- ---- 0000 0000 ==== ==== 
    ==== ==== ==== ==== 0000 0000 0000 0000 
    dddd dddd CCCC CCCC 0000 0000 0000 0000 
```
**Spawnpoints**, which are about 0x40 in length:
+ `A` 0x04 has always been an offset pointing to a null string. I have seen a functional spawn not point to the string table, so it has nothing to do with the start of the string table.
    > 一直是指向空字符串的偏移量。 我已经看到一个功能生成不指向字符串表，所以它与字符串表的开始无关。
    > 整块"spawnpoint"组结束位置
+ `B` 0x08 is the numeric waypoint identifier based on the whole RMPA?  
    > 基于整个RMPA的数字航点标识符？  
+ The first set of floats is the spawnpoint itself, while the second set is where the spawned entity will "Look at".  
    > 第一组浮点数是派生点本身，而第二组浮点数是派生实体将“查看”的位置。
+ `d` 0x30 名字字串长度
+ `C` 0x34 is the offset to the spawn's name.
    > 生成名称的偏移量。