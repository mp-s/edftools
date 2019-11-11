# EDF's modding Tools

## Required: Python 3.6+

### Usage: ##   
- If Windows has a Python interpreter associated with .py, drag and drop supported.  
- Command Prompt:
    - using interpreter: `python <foo.py> <infile> [outfile]`
    - using launcher: `py -3 <foo.py> <infile> [outfile]`
- Example:
    - BVM:
        + BVM -> assembly script:  
        `python bvm_decompiler.py "mission.bvm"`   
        + assembly script -> BVM:  
         `python bvm_compiler.py "test.asm"`  
    - RMPA:
        - RMPA -> json:  
         `python rmpa_parser.py "test.rmpa"`   
        - json -> RMPA:  
         `python rmpa_builder.py "test-rmpa.json"`   
            - *supported:`"route type"`  ` "shape type"`  ` "spawnpoint type"`   
            - *camera type in json will ignore*  
            - *Recommended using sample-rmpa.json to generate*   
    - Target file are same path with source file.
  
  
### Extra Tool:
- AWE:
    - using "VGMToolbox" AWB Archive extractor, get extracted directory
    - then run "awe_parse.py", follow the prompts.

- Assisted coordinates mods:
    - **Cheat Table Required: Cheat Engine 7.0+**
    - ``` edf5-coordinates-test-github-public.zip ```  
    - ``` edf41-coordinates-test-github-public.zip ```  
        - test Missions list Assisted by AUK233  
  
- more Documents in Documents/  

- Chinese Only: _简易hex与浮点转换辅助_ &nbsp;:    
    _双击打开 `simple_ieee754_float_convert.py`_  

## Thanks
* [EDF's Discord Channel](https://discord.gg/bfGjgTM) #edf-modding community
    * [@KittopiaCreator's project](https://gitlab.com/kittopiacreator/edf-tools)  
    * [@Zeddy's project](https://github.com/zeddidragon/sgott)

- EDF Japanese anonymous Channel