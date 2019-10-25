# Python ported EDF Tools

## Required: Python 3.6+

## usage: ###   
- BVM:
    + BVM -> assembly script:  
    `python bvm_decompiler.py "r:\mission.bvm"`   
    + assembly script -> BVM:  
    `python bvm_compiler.py "r:\test.asm"`  
- RMPA:
    - RMPA -> json:  
    `python rmpa_parser.py "r:\test.rmpa"`   
    - *json -> rmpa:*  
    `python rmpa_parser.py "test-rmpa.json"`   
        > *only "spawnpoints type" generated*  

### Target file are same path with source file.
 **Only Chinese Extra Tool:**
- _简易hex与浮点转换辅助_ &nbsp;:    
    _双击打开 `simple_ieee754_float_convert.py`_  

## Thanks
* [EDF's Discord Channel](https://discord.gg/bfGjgTM) #edf-modding community
    * [@KittopiaCreator's project](https://gitlab.com/kittopiacreator/edf-tools)  
    * [@Zeddy's project](https://github.com/zeddidragon/sgott)

- EDF Japanese anonymous Channel