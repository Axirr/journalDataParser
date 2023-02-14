from myNewDataFormatList import getDataFormatList, getPublicDataFormats
from globalConstants import NEW_PARSER_INPUT_FILENAME, NEW_PARSER_OUTPUT_FILENAME, PARSER_NULL_VALUE, READ_PUBLIC_ONLY_ARG, PLAINTEXT_PUBLIC_OUTPUT_FILE
from sys import argv
import re

# Date bounds for daily entry parsing
earliestDate = "december 6, 2022"
latestDateNotInclusive = "february 14, 2023"

def main():
    f = open(NEW_PARSER_INPUT_FILENAME,'r')
    line = f.readline().lower()
    parsedData = []
    currentDate = ""

    if (len(argv) > 1 and READ_PUBLIC_ONLY_ARG in argv):
        dataFormatList = getPublicDataFormats()
    else:
        dataFormatList = getDataFormatList()

    logPrin("Parsing data from %s (inclusive) to %s (exclusive)." % (earliestDate, latestDateNotInclusive))
    logPrin('\n')

    # Header for CSV file
    topLine = createTopLine(dataFormatList)

    #
    dataFieldNames = topLine.split(",")

    # Traverse file until earliest data found
    #       Since may want to exclude datas that don't match format
    while (line):
        line = line.lower()
        if earliestDate in line:
            break
        line = f.readline()


    tabLevel = 0
    tabLineStacks = ["TOP LEVEL"]
    nonFieldLinesForTabLine = [[]]
    printStack = []
    previousLine = ""
    while (line):
        line = line.lower()
        line = line.replace('\n', "")

        oldTabLevel = tabLevel

        count = 0
        for letter in line:
            if letter == '\t':
                count += 1

        if len(nonFieldLinesForTabLine) > 0:
            nonFieldLinesForTabLine[-1].append(previousLine)
        if count < oldTabLevel:
            for i in range(oldTabLevel - count):
                try:
                    printStack.append([tabLineStacks.pop(), nonFieldLinesForTabLine.pop()])
                except:
                    pass
        elif count > oldTabLevel:
            tabLineStacks.append(previousLine)
            nonFieldLinesForTabLine.append([])

        if count > oldTabLevel and abs(oldTabLevel - count) > 1:
            logPrin("Tab level increased by more than one?")

        tabLevel = count

        if latestDateNotInclusive in line:
            break
        
        # Check for preliminary match for date using lowercase months
        # Ugly
        if tabLevel == 0:
            for month in ['january','february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']:
                workingLine = line
                if re.match(month, workingLine) != None and re.search("[0-9]{4}", workingLine):
                    workingLine = line
                    workingLine = workingLine.rstrip('\n')
                    workingLine = workingLine.replace(",", "")
                    workingLine = workingLine.replace(":", "")
                    splitLine = workingLine.split(" ")

                    # Data validity check after stripping
                    if len(splitLine) == 3:
                        # append data if date found, but only if not first date found
                        if currentDate != "":
                            dataDict['date'] = currentDate
                            resultList = []
                            for key in dataDict:
                                resultList.append(dataDict[key])
                            resultList[-1] = resultList[-1] + "\n"
                            parsedData.append(resultList)
                            while len(tabLineStacks) > 0:
                                printStack.insert(0, [tabLineStacks.pop(), nonFieldLinesForTabLine.pop()])
                            print()
                            print()
                            print("DAY START %s" % currentDate)
                            for printLine in printStack:
                                print(printLine)
                                print()
                        currentDate = workingLine
                        dataDict = {}
                        for dataname in dataFieldNames:
                            dataDict[dataname] = PARSER_NULL_VALUE
                        line = f.readline()
                        printStack = []
                        tabLineStacks = ["TOP LEVEL"]
                        nonFieldLinesForTabLine = [[]]
                        break
                    else:
                        logPrin("False alarm date")


        # Parse line looking for data format list entires and subformat entries
        resultDict = readDataFormatList(dataFormatList, f, line, currentDate, tabLineStacks)

        for key in resultDict:
            dataDict[key] = resultDict[key]

        previousLine = line
        line = f.readline()

    # Append last date's data
    if currentDate != "":
        dataDict['date'] = currentDate
        resultList = []
        for key in dataDict:
            resultList.append(dataDict[key])
        parsedData.append(resultList)
    mySplitLine = topLine.split(',')
    mySplitParsed = parsedData[-2]
    for i in range(len(mySplitLine)):
        print(mySplitLine[i], end = " ")
        print(mySplitParsed[i], end=" ")
        print(i)
    
    dataFieldNamesLength = len(topLine.split(','))

    # Write data to file
    if len(argv) > 1 and READ_PUBLIC_ONLY_ARG in argv:
        print("Saving to file %s" % PLAINTEXT_PUBLIC_OUTPUT_FILE)
        writeFile = open(PLAINTEXT_PUBLIC_OUTPUT_FILE, 'w')
    else:
        print("Saving to file %s" % NEW_PARSER_OUTPUT_FILENAME)
        writeFile = open(NEW_PARSER_OUTPUT_FILENAME, 'w')
    # writeFile = open("dailyDataTo" + currentDate + ".csv", 'w')
    writeFile.write(topLine + '\n')
    for line in parsedData:
        lineLength = len(line)
        # Check data in line for every heading fieldname
        assert lineLength == dataFieldNamesLength
        stringLine = ','.join(line)
        writeFile.write(stringLine)
    f.close()
    writeFile.close()

def isField(line, dataFormatList, currentDate, f):
    isField = False
    for dataFormat in dataFormatList:
        if dataFormat.searchName in line:
            return True
    return isField

def readDataFormatList(dataFormatList, f, line, currentDate, tabLineStacks):
    returnDict = {}
    for dataFormat in dataFormatList:
        if dataFormat.searchName in line:
            if dataFormat.lineInstructions[-1] == dataFormat.searchName:
                returnedData = parseMultiLine(dataFormat,f, currentDate, line)
                if (len(returnedData) == 2):
                    returnDict[returnedData[0]] = returnedData[1]
            else:
                currentAbove = tabLineStacks[-1]
                currentAbove = currentAbove.strip()
                currentAbove = currentAbove.rstrip('\t')
                currentAbove = currentAbove.lstrip('\t')
                currentAbove = currentAbove.rstrip(':')
                if currentAbove == dataFormat.lineInstructions[-1]:
                    returnedData = parseMultiLine(dataFormat,f, currentDate, line)
                    if (len(returnedData) == 2):
                        returnDict[returnedData[0]] = returnedData[1]
    return returnDict

def subListDataSearch(dataFormatList, f, line, currentDate):
    resultDict = {}
    firstLine = f.tell()
    for format in dataFormatList:
        ulCount = 1
        resultDict[format.finalName] = PARSER_NULL_VALUE
        while ulCount > 0:
            line = f.readline().lower()
            if "<ul>" in line:  ulCount += 1
            if "</ul>" in line:  ulCount -= 1
            line = line.lower()
            if format.searchName in line:
                returnedData = sharedDataParse(line, format.finalName, format.separator, currentDate, format.parseType)
                if len(returnedData) == 2:
                    resultDict[returnedData[0]] = returnedData[1]
                break
        f.seek(firstLine)
    return resultDict
    

def dataCommonStrip(workingLine, separator, removalList = []):
    try:
        startIndex = workingLine.index(separator)

        workingLine = workingLine[startIndex + len(separator):]
        workingLine = workingLine.lstrip()
        workingLine = workingLine.rstrip('\n')
        for item in removalList:
            workingLine = workingLine.replace(item,'')
        return workingLine
    except ValueError as e:
        logPrin(workingLine)
        raise Exception("ERROR: SEPARATOR NOT FOUND")

def sharedDataParse(line, fieldName, separator, currentDate, validType, useDefaultRemoval = True, isNullAllowed=True, customRemoval = []):
    resultList = []
    isParseError = False
    workingLine = ""
    removalList = customRemoval
    if fieldName == "EBreathingType":
        pass
    if useDefaultRemoval:
        removalList += ['<b>', '</b>', '<li>', '</li>', '<br />', '&nbsp;', ';', '\n'] 
    try:
        workingLine = dataCommonStrip(line, separator, removalList)
    except Exception as myE:
        logPrin(myE)
        isParseError = True
    if not isParseError:
        try:
            if validType == "float":
                float(workingLine)
                resultList.append(fieldName)
                resultList.append(workingLine)
            elif validType == "int":
                int(workingLine)
                resultList.append(fieldName)
                resultList.append(workingLine)
            elif validType == "bool":
                if workingLine in ['yes', 'y', '1']:
                    resultList.append(fieldName)
                    resultList.append('1')
                elif workingLine in ['no', 'n', '0']:
                    resultList.append(fieldName)
                    resultList.append('0')
                else:
                    raise("BOOL PARSE ERROR")
            elif validType == "string":
                resultList.append(fieldName)
                resultList.append(workingLine)
            else:
                logPrin("ERROR: UNRECOGNIZED TYPE %s", validType)
                exit()
        except:
            if workingLine == 'n/a':
                resultList.append(fieldName)
                resultList.append(workingLine)
            elif isNullAllowed and workingLine == "":
                # logPrin("null value written for %s on date %s" % (fieldName, currentDate))
                resultList.append(fieldName)
                resultList.append(PARSER_NULL_VALUE)
            else:
                isParseError = True
    else:
        isParseError = True
    if isParseError and fieldName not in ["eveningBreathingBool", "morningBreathingBool"]:
        logPrin("parse error for " + fieldName)
        logPrin(currentDate)
        logPrin(workingLine)
    return resultList

def parseMultiLine(lineFormat, f, currentDate, currentLine):
    workingLine = currentLine
    returnedData = sharedDataParse(workingLine, lineFormat.finalName, lineFormat.separator, currentDate, validType = lineFormat.parseType, customRemoval = lineFormat.customRemovalList)
    if (len(returnedData) == 2):
        returnedData[0] = lineFormat.finalName
        return returnedData
    return []

# Creates CSV header based on dataformat list (including subformats), without a new line
def createTopLine(dataFormatList):
    line = "date,"
    for i in range(len(dataFormatList)):
        data = dataFormatList[i]
        line += data.finalName + ","
        for j in range(len(data.subDataFormats)):
            innerData = data.subDataFormats[j]
            line += innerData.finalName + ","
    line = line[:-1]
    return line

def logPrin(myStr, end='\n'):
    return
    print(myStr, end)

if __name__ == "__main__":
    main()