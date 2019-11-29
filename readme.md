# EDF's modding Tools

## Required: Python 3.6+

### Usage: ##   
- If Windows has a Python interpreter associated with .py:
    - drag and drop to `.py` supported.  
    - run `.py` and drag input file supported.  
- Command Prompt:
    - using interpreter: `python <foo.py> [args]`
    - using launcher: `py -3 <foo.py> [args]`
    ```
    usage: *foo*.py [-h] [-d] [-t] [source_path] [destination_path]

    positional arguments: *optional
      source_path       input file path
      destination_path  output file path

    optional arguments:
      -h, --help        show this help message and exit
      -d, --debug       enable debug mode
      -t
    ```
| Executable tool |
|------------------|
| bvm_compiler.py   |
| bvm_decompiler.py |
| rmpa_parser.py    |
| rmpa_builder.py   |

- Dependent file
    bvm_model.py  
    common_utils.py  
    rmpa_config.py  



- ***About RMPA_builder:***  
        - *supported:`"route type"`  ` "shape type"`  ` "spawnpoint type"`   
        - *camera type in json will ignore*  
        - *Recommended using sample-rmpa.json to generate*   
  
### Extra Tool:
- AWE:
    - using `VGMToolbox` AWB Archive extractor, get extracted directory
    - then run `awe_parse.py`, follow the prompts.


- RAB and MRAB ***extract only***:
    -   ```
        usage: rab_exract.py [-i INPUT] [source_path]

        RAB Extractor

        positional arguments:
        source_path                 RAB file path

        optional arguments:
        -i INPUT, --input INPUT     RAB file path
        ```  


- Assisted coordinates mods:
    - **Cheat Table Required: Cheat Engine 7.0+**
    - ``` edf5-coordinates-test-github-public.zip ```  
    - ``` edf41-coordinates-test-github-public.zip ```  
        - test Missions list Assisted by AUK233  
  
- asm file more function comments:  
    - `asm_more_readable.py foo.asm`  
- more Documents in Documents/  

- Only Chinese: _简易hex与浮点转换辅助_ &nbsp;:    
    _双击打开 `simple_ieee754_float_convert.py`_  

## Thanks
* [EDF's Discord Channel](https://discord.gg/bfGjgTM) #edf-modding community
    * [@KittopiaCreator's project](https://gitlab.com/kittopiacreator/edf-tools)  
    * [@Zeddy's project](https://github.com/zeddidragon/sgott)

- EDF Japanese anonymous Channel
