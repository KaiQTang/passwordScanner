import os
import subprocess

types = ['txt','log']
keywords = ['password','passwd']
result = {}

def main():
    files = []
    for type in types:
        files.extend(addFiles(type))
        addFiles(type)

    print("scan through following files: " + str(files))
    patterns = loadPatterns()
    for file in files:
        openAndScan(file, patterns)

    if (result == {}):
        print("nothing is found, good job! =.=")
    else:
        for file,findings in result.items():
            print(file + ": " +str(len(findings)))
            for finding in findings:
                print(finding)

def addFiles(type):
    all = "bash -c \"find . -name \'*." + type + "\'\""
    result = subprocess.check_output(all)
    result = result.strip()
    result = result.split('\n')
    return result

def openAndScan(file, patterns):
    if(file != './patterns.txt' and file != ''):
        with open(file) as fp:
            line = fp.readline()
            count = 1
            while line:
                findAndSendToResult(line, count, patterns, file)
                line = fp.readline()
                count += 1

def findAndSendToResult(line, count, patterns, file):
    for keyword in keywords:
        index = line.find(keyword)
        if (index != -1):
            matchFlag = False
            for pattern in patterns:
                if (pattern[0:len(keyword)] == keyword):
                    searchTo = len(pattern) - len(keyword)
                    if (line[index:index+len(keyword)+searchTo] == pattern):
                        matchFlag = True
                        pass
            if (not matchFlag):
                addToResult(file, line, index, count)

def loadPatterns():
    with open('patterns.txt') as f:
        patterns = f.read().splitlines()
    return patterns

def addToResult(file, line, index, count):
    res = (str(count) + " : " + line[index:])
    if (result.get(file) == None):
        result[file] = []
        result[file].append(res)
    else:
        if (res not in result[file]):
            result[file].append(res)

if __name__ == '__main__':
    main()