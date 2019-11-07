# Python ported EDF Tools

## Required: Python 3.6+

## example: ##   
- Command Prompt:
    - BVM:
        + BVM -> assembly script:  
        `python bvm_decompiler.py "r:\mission.bvm"`   
        + assembly script -> BVM:  
        `python bvm_compiler.py "r:\test.asm"`  
    - RMPA:
        - RMPA -> json:  
        `python rmpa_parser.py "r:\test.rmpa"`   
        - *json -> rmpa:*  
        `python rmpa_builder.py "test-rmpa.json"`   
            > **other types in json will crash**  
            > *only "spawnpoints type" generated*  
            > ***Recommended using sample-rmpa.json to generate***   
- If Windows has a Python interpreter associated with .py, drag and drop supported

### Target file are same path with source file.
 **Only Chinese Extra Tool:**
- _简易hex与浮点转换辅助_ &nbsp;:    
    _双击打开 `simple_ieee754_float_convert.py`_  

## Thanks
* [EDF's Discord Channel](https://discord.gg/bfGjgTM) #edf-modding community
    * [@KittopiaCreator's project](https://gitlab.com/kittopiacreator/edf-tools)  
    * [@Zeddy's project](https://github.com/zeddidragon/sgott)

- EDF Japanese anonymous Channel