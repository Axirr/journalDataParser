from privateSrc.privateDataFormatList import *
from src.globalConstants import *
from sys import argv
import re
from time import sleep
from datetime import date

def main(isPublic = False):
    if (len(argv) > 1 and READ_PUBLIC_ONLY_ARG in argv):  isPublic = True
    print(argv)

    if (isPublic):
        print("Reading public data types ONLY")
        dataFormatList = getPublicDataFormats()
        uniqueFinalNameDataFormats = publicGetUniqueFinalNameDataFormats()
    else:
        print("Reading all data types, not just public")
        dataFormatList = getDataFormatList()
        uniqueFinalNameDataFormats = getUniqueFinalNameDataFormats()
    #sleep(2)
    
    todayDate = date.today()
    automaticEndDate = todayDate.strftime("%B %d, %Y").replace(" 0", " ").lower()
    print("Reading up to (but not including) today's date (%s)" %automaticEndDate)
    print()
    #sleep(2)



    # Header for CSV file
    print("length dataFormats %d" % len(dataFormatList))
    print("length unqiue dataFormats %d" % len(uniqueFinalNameDataFormats))
    topLine = createTopLine(uniqueFinalNameDataFormats)

    parsedData = []
    for i in range(len(PLAINTEXT_INPUT_FILES)):
        currentFileName = PLAINTEXT_INPUT_FILES[i]
        currentEarliestDate = EARLIEST_DATE_FOR_FILE[i]
        firstNotIncludedDate = automaticEndDate
        if (i + 1 < len(PLAINTEXT_INPUT_FILES)):  firstNotIncludedDate = EARLIEST_DATE_FOR_FILE[i + 1]
        print("Current file name %s from start date %s to end date (non inclusive) %s" % (currentFileName, currentEarliestDate, firstNotIncludedDate))
        resultParsedData = readForFile(currentFileName, dataFormatList, topLine, currentEarliestDate, firstNotIncludedDate)
        print("Last line of output", end="")
        print(resultParsedData[-1])
        parsedData = parsedData + resultParsedData
        parsedData[-1][-1] += '\n'
    dataFieldNamesLength = len(topLine.split(','))

    # Write data to file
    if isPublic:
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
    writeFile.close()

def readForFile(currentFileName, dataFormatList, topLine, currentEarliestDate, firstNotIncludedDate):
    try:
        f = open(currentFileName,'r')
    except OSError:
        print("Could not open file %s" % currentFileName)
        raise FileNotFoundError()
    currentDate = ""
    line = f.readline().lower()
    parsedData = []

    dataFieldNames = topLine.split(",")

    # Traverse file until earliest data found
    #       Since may want to exclude datas that don't match format
    while (line):
        line = line.lower()
        if currentEarliestDate in line:
            print("earliest data %s found!" % currentEarliestDate)
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
                tempList = [tabLineStacks.pop(), nonFieldLinesForTabLine.pop()]
                printStack.append(tempList)
        elif count > oldTabLevel:
            tabLineStacks.append(previousLine)
            nonFieldLinesForTabLine.append([])

        if count > oldTabLevel and abs(oldTabLevel - count) > 1:
            logPrin("Tab level increased by more than one?")

        tabLevel = count

        if firstNotIncludedDate in line:
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
            # print("key %s value %s" % (key, resultDict[key]))
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

    f.close()
    return parsedData

def isField(line, dataFormatList, currentDate, f):
    isField = False
    for dataFormat in dataFormatList:
        if dataFormat.searchName in line:
            return True
    return isField

def readDataFormatList(dataFormatList, f, line, currentDate, tabLineStacks):
    returnDict = {}
    for dataFormat in dataFormatList:
        searchNameRegularExpression = re.escape(dataFormat.searchName)
        # if dataFormat.searchName in line:
        if re.search(searchNameRegularExpression, line) != None:
            if dataFormat.lineInstructions[-1] == dataFormat.searchName:
                returnedData = parseMultiLine(dataFormat,f, currentDate, line)
                if (len(returnedData) == 2):
                    returnDict[returnedData[0]] = returnedData[1]
                    # Break on successful match assumes you cannot validly find two data points in one line
                    break
            else:
                currentAbove = tabLineStacks[-1]
                # print("BUG WARNING, THIS COULD BREAK THINGS")
                # if currentAbove == dataFormat.lineInstructions[-1]:
                regExpForParent = re.escape(dataFormat.lineInstructions[-1])
                if re.search(regExpForParent, currentAbove):
                # if dataFormat.lineInstructions[-1] in currentAbove:
                    returnedData = parseMultiLine(dataFormat, f, currentDate, line)
                    if (len(returnedData) == 2):
                        returnDict[returnedData[0]] = returnedData[1]
                        # Break on successful match assumes you cannot validly find two data points in one line
                        break
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
    # if fieldName == "EBreathingType":
    #     pass
    if useDefaultRemoval:
        removalList += ['<b>', '</b>', '<li>', '</li>', '<br />', '&nbsp;', ';', '\n'] 
    try:
        workingLine = dataCommonStrip(line, separator, removalList)
    except Exception as myE:
        logPrin(myE)
        isParseError = True
    if not isParseError:
        try:
            if validType == FLOAT_DATA_TYPE:
                float(workingLine)
                resultList.append(fieldName)
                resultList.append(workingLine)
            elif validType == INT_DATA_TYPE:
                int(workingLine)
                resultList.append(fieldName)
                resultList.append(workingLine)
            elif validType == BOOL_DATA_TYPE:
                yesRegExp = [re.escape('yes'), re.escape('y'), re.escape('1')]
                noRegExp = [re.escape('no'), re.escape('n'), re.escape('0')]
                isFound = False
                for regExp in yesRegExp:
                    if re.search(regExp, workingLine) != None:
                # if workingLine in ['yes', 'y', '1']:
                        resultList.append(fieldName)
                        resultList.append('1')
                        isFound = True
                        break
                if not isFound:
                    # workingLine in ['no', 'n', '0']:
                    for regExp in noRegExp:
                        if re.search(regExp, workingLine) != None:
                            resultList.append(fieldName)
                            resultList.append('0')
                            isFound = True
                            break
                if not isFound:
                    print("line %s" % line)
                    print("currentDate %s" % currentDate)
                    print("workingLine %s" % workingLine)
                    print("BOOL PARSE ERROR")
            elif validType == HOUR_MINUTE_STRING:
                hourMinutePattern = '[0-9]+h[0-9]+m?'
                if (re.search(hourMinutePattern, workingLine) != None):
                    myHourSplitLine = workingLine.split('h')
                    hourString = myHourSplitLine[0]
                    minuteString = myHourSplitLine[1].lstrip("m")
                    minutes = str(int(hourString) * 60 + int(minuteString))
                    resultList.append(fieldName)
                    resultList.append(minutes)
                else:
                    print("hour minute parse error")
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
    # if isParseError and fieldName not in ["eveningBreathingBool", "morningBreathingBool"]:
    if isParseError:
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

    # Remove duplicate names
    # dataFormatList = list(set(dataFormatList))

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
    print("Module file. Should not be run directly.")
    main()