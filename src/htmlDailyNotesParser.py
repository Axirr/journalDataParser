from privateSrc.myDataFormatList import getDataFormatList, getPublicDataFormats
from src.globalConstants import PARSER_INPUT_FILENAME, PARSER_OUTPUT_FILENAME, PARSER_NULL_VALUE, READ_PUBLIC_ONLY_ARG, HTML_PUBLIC_OUTPUT_FILE
import re
from sys import argv

# Date bounds for daily entry parsing
earliestDate = "september 11, 2022"
latestDateNotInclusive = "december 6, 2022"

doConvertOldDataToNewDataFormat = True

hoursToMinutesFields = {
    'productiveHours': 'productiveMinutes',
    'programmingHours': 'programmingMinutes',
    'walkingHours': 'walkingMinutes',
    'socialHours': 'socialMinutes',
    'recreationHours': 'recreationMinutes',
    'gameHours': 'gameMinutes',
    'TVHours': 'TVminutes',
    'readingHours': 'readingMinutes',
    'activeHours': 'activeMinutes',
}

reverseRatingFields = {
    'wakeupTirednessRating': 'wakeupRestednessRating'
}

convertZeroThreeToZeroSix = {
    'insomniaRating': 'insomniaRating',
    'clarityRating': 'clarityRating',
    'productivityRating': 'productivityRating'
}

def main(isPublic = False):
    f = open(PARSER_INPUT_FILENAME,'r')
    line = f.readline().lower()
    parsedData = []
    currentDate = ""

    if (isPublic):
    # if (len(argv) > 1 and READ_PUBLIC_ONLY_ARG in argv):
        dataFormatList = getPublicDataFormats()
    else:
        dataFormatList = getDataFormatList()
    for format in dataFormatList: print(format.finalName)

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


    # indentLines = []
    # previousLine = ""
    while (line):
        line = line.lower()

        if latestDateNotInclusive in line:
            break
        
        # Check for preliminary match for date using lowercase months
        # Ugly
        for month in ['january','february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']:
            workingLine = line.replace('<li>','')
            if re.match(month, workingLine) != None and re.search("[0-9]{4}", workingLine):
                workingLine = line
                workingLine = workingLine.rstrip('\n')
                workingLine = workingLine.replace("li", "")
                workingLine = workingLine.replace("<", "")
                workingLine = workingLine.replace(">", "")
                workingLine = workingLine.replace("/", "")
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
                    currentDate = workingLine
                    dataDict = {}
                    for dataname in dataFieldNames:
                        dataDict[dataname] = PARSER_NULL_VALUE
                    line = f.readline()
                    break
                else:
                    logPrin("False alarm date")

        # Parse line looking for data format list entires and subformat entries
        resultDict = readDataFormatList(dataFormatList, f, line, currentDate)

        for key in resultDict:
            dataDict[key] = resultDict[key]

        previousLine = line
        line = f.readline()
    
    if doConvertOldDataToNewDataFormat:
        tempLine = topLine.split(',')
        for i in range(len(tempLine)):
            item = tempLine[i]
            if item in hoursToMinutesFields:
                tempLine[i] = hoursToMinutesFields[item]
            elif item in reverseRatingFields:
                tempLine[i] = reverseRatingFields[item]
            elif item in convertZeroThreeToZeroSix:
                tempLine[i] = convertZeroThreeToZeroSix[item]
        topLine = ','.join(tempLine)

    # Append last date's data
    if currentDate != "":
        dataDict['date'] = currentDate
        resultList = []
        for key in dataDict:
            resultList.append(dataDict[key])
        # resultList[-1] = resultList[-1] + "\n"
        parsedData.append(resultList)

    mySplitLine = topLine.split(',')
    mySplitParsed = parsedData[-2]
    for i in range(len(mySplitLine)):
        print(mySplitLine[i], end = " ")
        print(mySplitParsed[i], end=" ")
        print()
    # print(parsedData[-2])
    # printIndex = 7
    # print(topLine.split(',')[printIndex])
    # print(parsedData[-2][printIndex])
    # print(parsedData[-1][printIndex])
    
    dataFieldNamesLength = len(topLine.split(','))

    # Write data to file
    if (READ_PUBLIC_ONLY_ARG in argv):
        print("Saving to %s" % HTML_PUBLIC_OUTPUT_FILE)
        writeFile = open(HTML_PUBLIC_OUTPUT_FILE, 'w')
    else:
        print("Saving to %s" % PARSER_OUTPUT_FILENAME)
        writeFile = open(PARSER_OUTPUT_FILENAME, 'w')
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


def readDataFormatList(dataFormatList, f, line, currentDate):
    returnDict = {}
    for dataFormat in dataFormatList:
        if dataFormat.searchName in line:
            returnedData = parseMultiLine(dataFormat,f, currentDate, line)
            if (len(returnedData) == 2):
                returnDict[returnedData[0]] = returnedData[1]
            if len(dataFormat.subDataFormats) > 0:
                oldLine = f.tell()
                line = f.readline()
                if "<ul>" in line:
                    # line = f.readline().lower()
                    # subDataDict = readDataFormatList(dataFormat.subDataFormats, f, line, currentDate, listBounds = True)
                    subDataDict = subListDataSearch(dataFormat.subDataFormats, f, line, currentDate)
                    pass
                    for key in subDataDict:
                        returnDict[key] = subDataDict[key]
                else:
                    f.seek(oldLine)
    return returnDict

def subListDataSearch(dataFormatList, f, line, currentDate):
    resultDict = {}
    # line = f.readline().lower()
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
                if doConvertOldDataToNewDataFormat:
                    if fieldName in hoursToMinutesFields:
                        workingLine = str(int(60 * float(workingLine)))
                        # fieldName = hoursToMinutesFields[fieldName]
                resultList.append(fieldName)
                resultList.append(workingLine)
            elif validType == "int":
                int(workingLine)
                if doConvertOldDataToNewDataFormat:
                    if fieldName in reverseRatingFields:
                        oldRatings = [0,1,2,3]
                        newRatings = ['0','5','3','1']
                        value = int(workingLine)
                        if value in oldRatings:
                            workingLine = newRatings[oldRatings.index(value)]
                        else:
                            print("ERROR reversing field")
                            exit()
                    if fieldName in convertZeroThreeToZeroSix:
                        oldRatings = [1,2,3]
                        # newRatings = ['2','4','6']
                        newRatings = ['1','3','5']
                        value = int(workingLine)
                        if value in oldRatings:
                            workingLine = newRatings[oldRatings.index(value)]
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
    verbose = False
    workingLine = currentLine
    oldPosition = f.tell()
    currentLineFormat = lineFormat.lineInstructions
    for i in range(len(currentLineFormat)):
        searchStr = currentLineFormat[i]
        if not searchStr == "":
            if searchStr in workingLine:
                # Support for multiple search depth
                if (i == len(currentLineFormat) - 1):
                    returnedData = sharedDataParse(workingLine, lineFormat.finalName, lineFormat.separator, currentDate, validType = lineFormat.parseType, customRemoval = lineFormat.customRemovalList)
                    if (len(returnedData) == 2):
                        returnedData[0] = lineFormat.finalName
                        return returnedData
                    else:
                        break
            elif i == len(currentLineFormat) - 1:
                logPrin("Error on FINAL search finding %s" % searchStr)
                logPrin(currentDate)
                logPrin(workingLine, end="")
                break
            else:
                if verbose:
                    logPrin("NOT FOUND intermediate")
                    logPrin(searchStr)
                f.seek(oldPosition)
                break
        workingLine = f.readline().lower()
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
    print(myStr, end)


'''
Instead of using a list, need to use dictionary for several reasons
    Keep entries in order
    Put in automatic null values for entries that should always be present
        For CSV format, entries need to always be present anyways if they're ever to be inlcuded?
            To maintain column ordering
    
    Whenever find new day, populate dictionary for a bunch of keys
        keys=fieldNames
        value=nullValue, currently "null"
    Go through until next day starts
        Construct string to write to file, using predetermined key ordering


Simultaneous search for matches instead of repeated
    Some interesting algorithms to do it, but overbuilt for this currently

General solution to entires that are multiple lines long:
    Some seemingly single line entries are because of formatting (e.g. active hours)
    Need to potentially do:
        Skip lines
        Check subsequent lines for matches
            Multiple times potentially
        Reset back to proper line if searches were incorrect
    E.g. format:
        [fieldname, ["", "searchKey", ...]]
            "" indicates skip a line
            "searchKey" indicates something that has to match

Class implemented

Weirdness with dictionary currently holding classes
Better:
    Simple list of classes to search, and search string is "firstName" of class


Converting old data to new data:
    Easy part: multiplying hours by 60 to get minutes
    Hard part: making grid align so I can just concat the two files
        Hard because:
            Without all the categories from new, there will be too few categories and they will be misaligned
    
    Possible solutions:
        Modify lines When writing to file
        Get new data format fieldnames (i.e. new topLine)
        Use old topline to determine what columns values mean
        Create line to be written by iterating through new line fields
            If field is missing, write null
    
    Downsides:
        Relies on newDataFormat, which may change and would be good to keep separate
            But if doesn't change with newDataFormat, won't be able to concat
    
    Alternative:
        Merely change field names
            Or don't even have to do that
        Read files separately in grapher, and do this work there
        Will have to create a dataframe through more than just concatenation, but should be doable
'''

if __name__ == "__main__":
    print("Module file. Should not be run directly.")
    main()