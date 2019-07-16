import os
import fnmatch
import sys
import glob
import argparse
import json
import re
import traceback

result = {}
filtered = 0

def main():
    global filtered
    print("----------------------STARTING------------------------------")

    parser = argparse.ArgumentParser(description="Password Scanner")
    parser.add_argument("-p")
    parser.add_argument("-c")
    parser.add_argument("-o")
    args, leftovers = parser.parse_known_args()

    if args.c is None:
        print ("Config file is not set, using default config:")
        print ("types = ['log','txt']")
        print ("keywords = ['password']")
        print ("known patterns = []")
        types = ['log', 'txt']
        keywords = ['password']
        patterns = []
    else:
        try:
            print ("Loading config.json")
            (types,keywords,patterns,raw) = loadJson(args.c)
        except Exception as e:
            traceback.print_exc()
            print(e)
            exit()


    if args.p is None:
        print ("Path is not set, using current dir as root dir")
    else:
        try:
            print ("Change to path : " + str(args.p))
            oldPath = os.getcwd()
            os.chdir(args.p)
        except Exception as e:
            traceback.print_exc()
            print(e)
            exit()

    print("Gathering files with extensions: " + str(types))
    files = addFiles(types)

    print("------------Number of files to scan: " + str(len(files)) + "------------")

    print("Scanning for keywords: "+str(keywords))
    try:
        for file in files:
            print("Scanning : " + file)
            openAndScan(file, patterns, keywords)
    except Exception as e:
        traceback.print_exc()
        print("Failed to scan file " + str(file))
        print(e)

    print("\n")
    print("\n")
    print("----------------------RESULT------------------------------")
    count = 0
    if (result == {}):
        print("No sensitive information found for keywords " + str(keywords))
    else:
        for file,findings in result.items():
            print(file + ": " +str(len(findings)))
            for finding in findings:
                count = count + 1
                if len(finding)>100:
                    print(finding[0:100])
                else:
                    print(finding)
    print("------------Total number of findings: "+str(count)+"------------------")
    print("------------Hit on known patterns: " + str(filtered) + "------------------")
    if args.o is not None:
        print("------------Generating output json file------------------")
        os.chdir(oldPath)
        with open(args.o, 'w') as fp:
            json.dump(result, fp)
        print("------------" + args.o + " is generated------------")

    print("------------Finished------------")

def addFiles(types):
    files = []
    for type in types:
        matches = []
        if (sys.version_info[0] == 2):
            for root, dirnames, filenames in os.walk(u'.'):
                print(root,dirnames,filenames)
                for filename in fnmatch.filter(filenames, '*.'+type):
                    print("Adding file :" + filename)
                    matches.append(os.path.join(root, filename))
        else:
            matches = glob.glob('**/*.' + type, recursive=True)
        files.extend(matches)
    return files



def openAndScan(file, patterns, keywords):
    with open(file) as fp:
        line = fp.readline()
        count = 1
        while line:
            findAndSendToResult(line, count, patterns, file, keywords)
            line = fp.readline()
            count += 1

def findAndSendToResult(line, count, patterns, file, keywords):
    global filtered
    for keyword in keywords:
        index = [m.start() for m in re.finditer(keyword, line)]
        matches = []
        if (len(index) == 1):
            matches.append(line[index[0]:])
        if (len(index) > 1):
            counter = 1
            max = len(index)-1
            while (counter <= max):
                matches.append(line[index[counter-1]:index[counter]])
                counter += 1
            matches.append(line[index[max]:])

        if (matches != []):
            for match in matches:
                matchFlag = False
                if patterns != ['']:
                    for pattern in patterns:
                        if (pattern == ''):
                            pass
                        elif (bool(re.search(pattern, match))):
                            matchFlag = True
                            filtered += 1
                    if (not matchFlag):
                        addToResult(file, match, index, count)
                else:
                    addToResult(file, match, index, count)

def addToResult(file, line, index, count):
    res = ("line " + str(count) + " : " + line)
    if (result.get(file) == None):
        result[file] = []
        result[file].append(res)
    else:
        if (res not in result[file]):
            result[file].append(res)

def loadJson(file):
    with open(file, 'r') as f:
        config = json.load(f)
    for key, value in config.items():
        if key == 'types':
            types = value
        elif key == 'keywords':
            keywords = value
        elif key == 'patterns':
            patterns = value
        else:
            print("Extra item " + str(key) + " in config.json")
    return (types, keywords, patterns,config)


if __name__ == '__main__':
    main()
