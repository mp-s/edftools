# EDF's modding Tools

## Required: Python 3.6+

## example: ##   
- Command Prompt:
    - BVM:
        + BVM -> assembly script:  
        using interpreter: `python bvm_decompiler.py "r:\mission.bvm"`   
        using launcher: `py -3 bvm_decompiler.py "r:\mission.bvm"`   
        + assembly script -> BVM:  
        using interpreter: `python bvm_compiler.py "r:\test.asm"`  
        using launcher: `py -3 bvm_compiler.py "r:\test.asm"`  
    - RMPA:
        - RMPA -> json:  
        using interpreter: `python rmpa_parser.py "r:\test.rmpa"`   
        using launcher: `py -3 rmpa_parser.py "r:\test.rmpa"`   
        - *json -> rmpa:*  
        using interpreter: `python rmpa_builder.py "test-rmpa.json"`   
        using launcher: `py -3 rmpa_builder.py "test-rmpa.json"`   
            > **other types in json will crash**  
            > *only "shapes type" and "spawnpoints type" generated*  
            > ***Recommended using sample-rmpa.json to generate***   
- If Windows has a Python interpreter associated with .py, drag and drop supported.  


### Target file are same path with source file.
 **Extra Tool:**
- AWE:
    - using "VGMToolbox" AWB Archive extractor, get extracted directory
    - then run "awe_parse.py", follow the prompts.

- Only Chinese: _简易hex与浮点转换辅助_ &nbsp;:    
    _双击打开 `simple_ieee754_float_convert.py`_  

## Thanks
* [EDF's Discord Channel](https://discord.gg/bfGjgTM) #edf-modding community
    * [@KittopiaCreator's project](https://gitlab.com/kittopiacreator/edf-tools)  
    * [@Zeddy's project](https://github.com/zeddidragon/sgott)

- EDF Japanese anonymous Channel