# passwordScanner
User this python program to scan potential password/token leak in log files

User this python file to scan potential password/token leak in log files

# Installation
```
python -m pip install -r requirements.txt
```

# How to use: <br/>
Command Line:<br/>
```
python scanner.py -c config.json -p /root/logs -o output.json
```
GUI:<br/>
```
python gui.py
```

# Config.json format

{"patterns": ["password='fakepassword"], "types": ["txt", "log"], "keywords": ["refresh_token", "password"]}<br/>

types: file types to scan <br/>
keywords: keywords to find<br/>
patterns: known patterns, will not shown in result<br/>
Patterns are filtered out using regular expression, so if you want to filter out \
the exact word `password="**"`, Please use `password=\"[*][*]\"` because * is a special character in regular expression.\
Also `"` must be added as `\"` otherwise it will break the json format.
