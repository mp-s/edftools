# EDF's modding Tools

## Required: Python 3.6+

## Usage: ##   

### Mission Tools:  
Two methods:  
###### Using exe file: [release](https://github.com/mp-s/edftools/releases/latest)
###### Using mission_tools.py file
- If Windows has a Python interpreter associated with `.py`, you can:
    - drag and drop to `mission_tools.py`  
    - run `mission_tools.py` and drag input file.  
- Command Prompt:  
    - using interpreter: `python mission_tools.py [args]`  
    - using launcher: `py -3 mission_tools.py [args]`  
    - help message:  
        ```
        usage: mission_tools.py [-h] [-d] [source_path] [destination_path]

        bvm/rmpa/json/asm converter

        positional arguments:
        source_path       input file path
        destination_path  output file path

        optional arguments:
        -h, --help        show this help message and exit
        -d, --debug       enable debug mode
        ```
- Single Executable tool :

    - bvm_compiler.py    
    - bvm_decompiler.py  
    - rmpa_parser.py     
    - rmpa_builder.py    

- Dependency file  
    - bvm_model.py  
    - common_utils.py  
    - rmpa_config.py  
    - asm_more_readable.py  
  
  
  
- ***About RMPA_builder:***  
        - *supported:`"route type"`  ` "shape type"`  ` "spawnpoint type"`   
        - *camera type in json will ignore*  
        - *Recommended using sample-rmpa.json to generate*   
  
### Extra Tool:
- .AWE and .AWB file:
    - If Windows has a Python interpreter associated with .py:  
        - run `.py` and drag input file supported.  
    - command prompt help:
        ```
        usage: awe_parser.py [-h] [--awe AWE] [--awb AWB] [--o O] [awe_path] [awb_path] [output_path]

        edf's awe AND awb extractor

        positional arguments:
        awe_path     awe file path
        awb_path     awb file path
        output_path  output path (optional)

        optional arguments:
        -h, --help   show this help message and exit
        --awe AWE    awe file path
        --awb AWB    awb file path
        --o O        output path (optional)
        ```


- .RAB or .MRAB file ***extract only***:
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
  

- more Documents in Documents/  

- Only Chinese: _简易hex与浮点转换辅助_ &nbsp;:    
    _双击打开 `simple_ieee754_float_convert.py`_  

## Thanks to
* [EDF's Discord Channel](https://discord.gg/bfGjgTM) #edf-modding community
    * [@KittopiaCreator's project](https://gitlab.com/kittopiacreator/edf-tools)  
    * [@Zeddy's project](https://github.com/zeddidragon/sgott)

- EDF Japanese anonymous Channel
