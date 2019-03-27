import os
import subprocess
import platform
import fnmatch
import sys

types = ['log']
keywords = ['password','passwd']
result = {}

def main():
    print("----------------------STARTING------------------------------")
    files = []
    print("Gathering files with extensions: " + str(types))
    for type in types:
        files.extend(addFiles(type))

    print("Loading patterns from patterns.txt")
    patterns = loadPatterns()
    print("Scanning for keywords: "+str(keywords))
    for file in files:
        try:
            print("Scanning on: " + file)
            openAndScan(file, patterns)
        except:
            print("Cannot scan on file: " + file)
            pass

    print("----------------------RESULT------------------------------")
    count = 0
    if (result == {}):
        print("No sensitive information found for keywords " + str(keywords))
    else:
        for file,findings in result.items():
            print(file + ": " +str(len(findings)))
            for finding in findings:
                count = count + 1
                print(finding)
    print("------------Total number of findings: "+str(count)+"------------------")
    sys.exit(count)

def addFiles(type):
    matches = []
    for root, dirnames, filenames in os.walk(u'.'):
        print(root,dirnames,filenames)
        for filename in fnmatch.filter(filenames, '*.'+type):
            print("Adding file :" + filename)
            matches.append(os.path.join(root, filename))
    return matches



def openAndScan(file, patterns):
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
