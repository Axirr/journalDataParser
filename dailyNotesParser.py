from dataFormatList import getDataFormatList, earliestDate, latestDate
import re

NULL_VALUE = "null"
OUTPUT_FILENAME = "output.csv"
INPUT_FILENAME = 'daily2022export.nnex'

'''
Example data formats:
earliestDate = "september 11, 2022"
latestDate = "november 14, 2022"
'''

def main():
    f = open(INPUT_FILENAME,'r')
    line = f.readline().lower()
    parsedData = []
    currentDate = ""

    dataFormatList = getDataFormatList()

    logPrin("Parsing data from %s (inclusive) to %s (exclusive)." % (earliestDate, latestDate))
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


    while (line):
        line = line.lower()

        if latestDate in line:
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
                        dataDict[dataname] = NULL_VALUE
                    line = f.readline()
                    break
                else:
                    logPrin("False alarm date")

        # Parse line looking for data format list entires and subformat entries
        resultDict = readDataFormatList(dataFormatList, f, line, currentDate)

        for key in resultDict:
            dataDict[key] = resultDict[key]

        line = f.readline()

    # Append last date's data
    if currentDate != "":
        resultList = []
        for key in dataDict:
            resultList.append(dataDict[key])
        resultList[-1] = resultList[-1] + "\n"
        parsedData.append(resultList)
    
    dataFieldNamesLength = len(topLine.split(','))

    # Write data to file
    writeFile = open(OUTPUT_FILENAME, 'w')
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
                # Subdata parsing contingent on successfully getting top level data
                #   may be an issue since some top levels don't have data
                if len(dataFormat.subDataFormats) > 0:
                    oldLine = f.tell()
                    line = f.readline()
                    subDataDict = readDataFormatList(dataFormat.subDataFormats, f, line, currentDate)
                    for key in subDataDict:
                        returnDict[key] = subDataDict[key]
    return returnDict
    

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

def sharedDataParse(line, fieldName, separator, currentDate, useDefaultRemoval = True, validType = "float", isNullAllowed=True, customRemoval = []):
    resultList = []
    isParseError = False
    workingLine = ""
    removalList = customRemoval
    if useDefaultRemoval:
        removalList += ['<b>', '</b>', '<li>', '</li>', '<br />', '&nbsp;', ';'] 
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
                logPrin("null value written for %s on date %s" % (fieldName, currentDate))
                resultList.append(fieldName)
                resultList.append(NULL_VALUE)
            else:
                isParseError = True
    else:
        isParseError = True
    if isParseError:
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
                if verbose:  logPrin("NOT FOUND itermediate")
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
'''

main()