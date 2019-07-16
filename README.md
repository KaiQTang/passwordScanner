# passwordScanner
User this python program to scan potential password/token leak in log files\

Installation:\
python -m pip install -r requirements.txt \

Config file:\
Modify config.json for different file types and keywords.\
Patterns are filtered out using regular expression, so if you want to filter out \
the exact word `password="**"`, Please use `password=\"[*][*]\"` because * is a special character in regular expression.\
Also `"` must be added as `\"` otherwise it will break the json format.\

Usages:\
GUI version : run `python gui.py`.\
Non-GUi : run `python scanner.py -c E:\dev\passwordscanner\config.json -p E:\dev\passwordscanner\log -o output.json`\
where -c points to the config.json, -p points to scan location and -o is for output location.\
