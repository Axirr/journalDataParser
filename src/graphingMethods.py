import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from privateSrc.privateDataFormatList import *
from src.globalConstants import *
from copy import copy
import os


def lineGraphWithOptions(currentFieldName, currentGraphName, originalDf, optionsDict, dataFormat, secondDF = None, dfToPlot=None, saveLocation=None, saveName=None):
    myDf = originalDf.copy(deep=True)
    print("Deleting keys on original optionals dict to ensure processing is bad, should remove or do on copy")

    checkInconsistentOptions(optionsDict)

    if currentGraphName != "test":
        currentGraphName = createTitleFromOptions(optionsDict, currentGraphName)

    ###
    # Individual data cleanup
    ###

    myDf[currentGraphName] = myDf[currentFieldName]

    myDf = dataCleanup(myDf, optionsDict, currentGraphName, dataFormat)

    # Aggregation
    # Groupings inconsistent with each other so are alternative and will cause error if both included
    # Establish X values
    hadDayOfWeek = False
    hadWeekly = False
    if not BOX_PLOT in optionsDict:
        if WEEK_FIELD in optionsDict:
            hadWeekly = True
            mySeries = myDf.groupby(WEEK_FIELD)[currentGraphName].mean()
            myDf = pd.DataFrame({DATE_FIELD: mySeries.index, currentGraphName: mySeries.values})
            del optionsDict[WEEK_FIELD]
        elif DAY_OF_WEEK in optionsDict:
            mySeries = myDf.groupby(DAY_OF_WEEK)[currentGraphName].mean()
            myDf = pd.DataFrame({DATE_FIELD: mySeries.index, currentGraphName: mySeries.values})
            hadDayOfWeek = True
            del optionsDict[DAY_OF_WEEK]
        elif MONTH_FIELD in optionsDict:
            mySeries = myDf.groupby(MONTH_FIELD)[currentGraphName].mean()
            myDf = pd.DataFrame({DATE_FIELD: mySeries.index, currentGraphName: mySeries.values})
            del optionsDict[MONTH_FIELD]
        
        if BAR_OPTION in optionsDict:
            mySeries = myDf.groupby(optionsDict[BAR_OPTION])[currentGraphName].mean()
            myDf = pd.DataFrame({DATE_FIELD: mySeries.index, currentGraphName: mySeries.values})

    yRangeTuple = (None, None)

    # If multi-plot, will automatically size to include max and min of both unless overridden
    # using Y_MIN or Y_MAX
    if not secondDF is None:
        bothMax = max(secondDF[secondDF.columns[1]].max(), myDf[currentGraphName].max())
        bothMin = min(secondDF[secondDF.columns[1]].min(), myDf[currentGraphName].min())
        yRangeTuple = (bothMin, bothMax)

    if Y_MAX in optionsDict:
        yRangeTuple = (yRangeTuple[0], optionsDict[Y_MAX])
        del optionsDict[Y_MAX]
    
    if Y_MIN in optionsDict:
        yRangeTuple = (optionsDict[Y_MIN], yRangeTuple[1])
        del optionsDict[Y_MIN]
    
    if MULTI_PLOT in optionsDict:
        myDf = myDf[[DATE_FIELD, currentGraphName]]
        return myDf

    # Plotting regular graph
    # if BAR_OPTION in optionsDict or hadDayOfWeek or hadWeekly:
    if BAR_OPTION in optionsDict:
        # if BAR_OPTION in optionsDict:
        #     del optionsDict[BAR_OPTION]
        if not secondDF is None:
            myDf = pd.merge(myDf, secondDF, on=DATE_FIELD)
            ax = myDf.plot.bar(x=DATE_FIELD, y=[myDf.columns[1], myDf.columns[2]])
        else:
            ax = myDf.plot.bar(x=DATE_FIELD, ylim=yRangeTuple)
        if hadDayOfWeek:
            dayNames = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
            ax.set_xticks(range(0,7))
            ax.set_xticklabels(dayNames)
    elif BOX_PLOT in optionsDict:
        myDf = myDf.boxplot(column=[currentFieldName], by=[optionsDict[BOX_PLOT]])
        ax = myDf.plot()
        # del optionsDict[BOX_PLOT]
    else:
        myDf = myDf[[DATE_FIELD, currentGraphName]]
        ax = myDf.plot(x=DATE_FIELD, ylim=yRangeTuple)
        if not secondDF is None:
            secondDF.plot(x=DATE_FIELD, y=secondDF.columns[1] ,ax=ax)
    
    # Plotting average line, if specified
    if AVG_LINE in optionsDict:
        del optionsDict[AVG_LINE]
        myAverage = myDf[currentGraphName].mean()
        plt.axhline(y=myAverage, color='r', linestyle='-')

    # Save plot and clear plot for next ones
    fileSaveName = currentFieldName + '.png'
    if fileSaveName != None:
        # allowedNames = [item.finalName for item in getPublicDataFormats()]
        # if saveName not in allowedNames:
        #     print("INVALID SAVE NAME")
        #     print("The name is %s" % saveName)
        #     return
        fileSaveName = saveName
    print("File savename is %s" % fileSaveName)

    saveLocation = os.environ.get('GRAPH_SAVE_LOCATION')
    if saveLocation == None:
        print("SAVE LOCATION ENVIRONEMNTAL VARIABLE NOT SET. ABORTING FILE SAVE")
    else:
        print("Saving to %s" % saveLocation)
        plt.savefig(saveLocation + fileSaveName)

    plt.clf()
    plt.cla()
    plt.close()

def graphMultiple(fieldNames, optionsDict, originalDf, filename):
    checkInconsistentOptions(optionsDict)

    myDf = originalDf.copy()
    myDataFormatList = getDataFormatList()

    for format in myDataFormatList:
        if format.finalName == fieldNames[0]:
            currentDataFormat = format
            break
    currentFieldName = fieldNames[0]
    myDf = dataCleanup(myDf, optionsDict, currentFieldName, currentDataFormat)

    for currentFieldName in fieldNames:
        for format in myDataFormatList:
            if format.finalName == currentFieldName:
                currentDataFormat = format
                break
        # newDf = lineGraphWithOptions(currentFieldName, currentFieldName, myDf, multiPlotOptionsDict, currentDataFormat)
        myDf = dataCleanup(myDf, optionsDict, currentFieldName, currentDataFormat)
    myDf = dropNonNameOrGroupColumns(fieldNames, optionsDict, myDf)
    if (not BOX_PLOT in optionsDict and not HISTOGRAM in optionsDict):
        myDf = groupAllByMaintainName(fieldNames, optionsDict, myDf)
    if (not HISTOGRAM in optionsDict):
        graphAllColumns(optionsDict, myDf, filename)
    else:
        print("graphing histogram")
        histogram(myDf, fieldNames[0], optionsDict, filename)

def dropNonNameOrGroupColumns(fieldNames, optionsDict, myDf):
    workingFieldNames = copy(fieldNames)
    workingFieldNames.append(getGroupColumnName(optionsDict))
    columnsToDrop = [col for col in myDf.columns if col not in workingFieldNames]
    # print("Columns to drop")
    # print(columnsToDrop)
    myDf = myDf.drop(columnsToDrop, axis=1)
    # for col in myDf.columns:
    #     if col not in workingFieldNames:
    #         myDf.drop(col)
    print(myDf.columns)
    return myDf

def groupAllByMaintainName(fieldNames, optionsDict, inputDf):
    groupField = getGroupColumnName(optionsDict)
    seriesArray = []
    for currentGraphName in fieldNames:
        mySeries = inputDf.groupby(groupField)[currentGraphName].mean()
        seriesArray.append(mySeries)
    constructedDf = pd.concat(seriesArray, axis=1)
    return constructedDf

def getGroupColumnName(optionsDict):
    groupField = DATE_FIELD
    if (WEEK_FIELD in optionsDict):
        groupField = WEEK_FIELD
    elif (MONTH_FIELD in optionsDict):
        groupField = MONTH_FIELD
    elif (DAY_OF_WEEK in optionsDict):
        groupField = DAY_OF_WEEK
    else:
        print("WARNING, NO VALID TIME GROUP FOUND")
    return groupField


def graphAllColumns(optionsDict, myDf, filename):
    yRangeTuple = (None, None)

    if Y_MAX in optionsDict:
        yRangeTuple = (yRangeTuple[0], optionsDict[Y_MAX])
        del optionsDict[Y_MAX]
    
    if Y_MIN in optionsDict:
        yRangeTuple = (optionsDict[Y_MIN], yRangeTuple[1])
        del optionsDict[Y_MIN]

    if (BAR_OPTION in optionsDict):
        # IMPLEMENT BAR OPTION
        ax = myDf.plot.bar(y=myDf.columns, use_index=True)
    elif (BOX_PLOT in optionsDict):
        # IMPLEMENT BOX OPTION
        myDf = myDf.boxplot(column=myDf.columns[0], by=[optionsDict[BOX_PLOT]])
        ax = myDf.plot()
    else:
        ax = myDf.plot(y=myDf.columns, ylim=yRangeTuple, use_index=True)
    
    if (REMOVE_LEGEND in optionsDict):
        ax.get_legend().remove()

    # IMPLEMENT AVG LINE? DOES IT MAKE SENSE FOR MULTIPLE DATA

    fileSaveName = filename

    if filename != None:
        # allowedNames = [item.finalName for item in getPublicDataFormats()]
        # allowedNames.append("multigraph.png")
        # if filename not in allowedNames:
        #     print("INVALID SAVE NAME")
        #     print("The name is %s" % filename)

        print("File savename is %s" % fileSaveName)
        saveLocation = os.environ.get('GRAPH_SAVE_LOCATION')
        if saveLocation == None:
            # print("Saving to globalConstants save location %s" % GRAPH_PATH_FROM_SRC)
            print("SAVE LOCATION ENVIRONEMNTAL VARIABLE NOT SET. ABORTING FILE SAVE")
        else:
            print("Saving to specified saveLocation %s" % saveLocation)
            plt.savefig(saveLocation + fileSaveName)

    plt.clf()
    plt.cla()
    plt.close()

def createTitleFromOptions(optionsDict, originalName):
    useValueKeys = [BAR_OPTION, BOX_PLOT, FIRST_DATE, LAST_DATE]
    useKeyOnly = [NULL_MEANS_MISSING, WEEK_FIELD, MONTH_FIELD, DAY_OF_WEEK, NO_WEEKEND, NORMALIZE]
    noTitleOptions = [MULTI_PLOT]
    dontUseKeys = set([NULL_MEANS_MISSING, NULL_IS_ZERO, MULTI_PLOT, AVG_LINE, Y_MAX,])

    for key in optionsDict:
        if key not in dontUseKeys:
            if not key in noTitleOptions:
                if key in useValueKeys:
                    originalName += optionsDict[key]
                elif key in useKeyOnly:
                    originalName += key
                else:
                    originalName += key + str(optionsDict[key])

    return originalName

def checkInconsistentOptions(optionsDict):
    groupOptions = [MONTH_FIELD, WEEK_FIELD, DAY_OF_WEEK]
    nanOptions = [NULL_IS_ZERO, NULL_MEANS_MISSING]

    inconsistentPairs = [
        [GRAPH_TYPES, GRAPH_TYPES],
        [groupOptions, groupOptions],
        [nanOptions, nanOptions],
        [[BOX_PLOT], [AVG_LINE, MULTI_PLOT]],
        # [GRAPH_TYPES, groupOptions],
        # [FIRST_DATE, FROM_FIRST_VALID_DATE],
    ]

    for pair in inconsistentPairs:
        options = pair[0]
        inconsistentOptions = pair[1]
        for option in options:
            for incOption in inconsistentOptions:
                if option != incOption:
                    if option in optionsDict and incOption in optionsDict:
                        raise(Exception("Inconsistent Options Error: %s and %s" % (option, incOption)))

def checkMandatoryOptions(optionsDict, mandatoryPairs):
    for pair in mandatoryPairs:
        options = pair[0]
        mandatoryOptions = pair[1]
        for option in options:
            if option in optionsDict:
                hasOption = False
                for incOption in mandatoryOptions:
                    if option != incOption:
                        if option in optionsDict and incOption in optionsDict:
                            hasOption = True
                            break
                if not hasOption:
                    raise(Exception("Mandatory Options Error " + str(options) + " " + str(mandatoryOptions)))

def dataCleanup(df, optionsDict, fieldName, dataFormat):
    myDf = df.copy()

    # Fill in blank data and then drop data in line with date and weekend constraints
    hasNullOption = NULL_MEANS_MISSING in optionsDict or NULL_IS_ZERO in optionsDict

    # BUG for graphing multiple series together, will only graph the intersection
    # I.e. will drop for each set
    # Is this desired behaviour?
    # Seems to do this even if I take the dropping out
    # Needs to be fixed in multiple places:
    #       null type check, first date check, grouping
    if NULL_MEANS_MISSING in optionsDict or (not hasNullOption and dataFormat.nullType == NULL_MEANS_MISSING):
        # myDf = myDf[myDf[fieldName].notnull()]

        myDf.drop(myDf[myDf[fieldName].isnull()].index, inplace=True)
    elif NULL_IS_ZERO in optionsDict or (not hasNullOption and dataFormat.nullType == NULL_IS_ZERO):
        # if FROM_FIRST_VALID_DATE in optionsDict:
        #     indexFirstValidDate = myDf[fieldName].ne(0).idxmax()
        #     if (isinstance(indexFirstValidDate,int)):
        #         print("First date index %d" % indexFirstValidDate)
        #         myDf.drop(myDf.index[0:max(indexFirstValidDate - 1, 0)], inplace=True)
        myDf[[fieldName]] = myDf[[fieldName]].fillna(0)
    else:
        print("Unrecognized nullType")
        exit()

    if FIRST_DATE in optionsDict:
        myDf.drop(myDf[myDf[DATE_FIELD] < optionsDict[FIRST_DATE]].index, inplace=True)
    else:
        # BUG don't want to automatically drop
        firstDate = myDf[myDf[fieldName].notnull()].iloc[0][DATE_FIELD]
        myDf.drop(myDf[myDf[DATE_FIELD] < firstDate].index, inplace=True)

    if LAST_DATE in optionsDict:
        myDf.drop(myDf[myDf[DATE_FIELD] > optionsDict[LAST_DATE]].index, inplace=True)

    if NO_WEEKEND in optionsDict:
        myDf.drop(myDf[myDf[DAY_OF_WEEK] > 5].index, inplace=True)


    # Data still around is what we want (e.g. no weekend) now modify as required with shift, normalize, average, etc.
    if SHIFT in optionsDict:
        # myDf[fieldName] = myDf[fieldName].shift(optionsDict[SHIFT])
        myDf[fieldName] = myDf[fieldName].shift(optionsDict[SHIFT])
    
    if NORMALIZE in optionsDict:
        stdDev = myDf[fieldName].std()
        if (stdDev == 0):  stdDev = 1
        # myDf[fieldName] = (myDf[fieldName]-myDf[fieldName].mean())/myDf[fieldName].std()
        myDf[fieldName] = (myDf[fieldName]-myDf[fieldName].mean())/ stdDev

    if ROLLING_AVERAGE in optionsDict:
        if optionsDict[ROLLING_AVERAGE] not in [0, 1]:
            myDf[fieldName] = myDf.rolling(window=optionsDict[ROLLING_AVERAGE])[fieldName].mean()
        else:
            print("Not using invalid rolling average value of %d." % optionsDict[ROLLING_AVERAGE])

    myDf = myDf[myDf[fieldName].notna()]
    
    return myDf


# Probably broken by changes to simple linear regression
# But not too hard to fix
# def doubleScatterPlot(xDataFormat, yDataFormat, xOptionsDict, yOptionsDict, globalOptionsDict, originalDf, firstDate = None, lastDate = None):
#     simpleLinearRegression(xDataFormat, yDataFormat, xOptionsDict, yOptionsDict, globalOptionsDict, originalDf, firstDate, lastDate)

# def simpleLinearRegression(xDataFormat, yDataFormat, xOptionsDict, yOptionsDict, globalOptionsDict, originalDf, firstDate = None, lastDate = None, scatter = False):
def simpleLinearRegression(xFieldName, yFieldName, xOptionsDict, yOptionsDict, globalOptionsDict, originalDf, firstDate = None, lastDate = None, scatter = False, filename=None):
    # Copy df to ensure not modified
    myDf = originalDf.copy()
    
    # Check that options are not inconsistent and are allowed for regression
    # Raises error if problem
    options = set(xOptionsDict.keys()) | set(yOptionsDict.keys()) | set(globalOptionsDict.keys())
    checkInconsistentOptions(options)
    # slrValidateOptions(options)

    if SHIFT in globalOptionsDict:
        raise(Exception("Shift cannot be a global option or it won't do anything"))
        exit()


    dataFormatList = getDataFormatList()
    xDataFormat = [format for format in dataFormatList if format.finalName == xFieldName][0]
    yDataFormat = [format for format in dataFormatList if format.finalName == yFieldName][0]

    # Not supported in Python < 3.9
    # mergedOptions = xOptionsDict | yOptionsDict
    # mergedOptions = mergedOptions | globalOptionsDict
    mergedOptions = { **xOptionsDict, **yOptionsDict }
    mergedOptions = { **mergedOptions, **globalOptionsDict}
    graphTitle = createTitleFromOptions(mergedOptions, "")

    for key in globalOptionsDict:
        xOptionsDict[key] = globalOptionsDict[key]
        # used to only add to xOptions
        yOptionsDict[key] = globalOptionsDict[key]

    myDf = dataCleanup(myDf, xOptionsDict, xFieldName, xDataFormat)
    myDf = dataCleanup(myDf, yOptionsDict, yFieldName, yDataFormat)

    # BUG Should make this process global to ensure only totally empty dates are dropped
    # rather than every date that is missing for one series being graphed
    myDf = groupAllByMaintainName([xFieldName, yFieldName], xOptionsDict, myDf)

    # Should unify grouping with linear graph grouping if possible, but it's not simple
    if WEEK_FIELD in globalOptionsDict:
        mySeries = myDf.groupby(WEEK_FIELD)[[xFieldName, yFieldName]].mean()
        myDf = pd.DataFrame({xFieldName: mySeries[xFieldName], yFieldName: mySeries[yFieldName]})
    elif MONTH_FIELD in globalOptionsDict:
        mySeries = myDf.groupby(MONTH_FIELD)[[xFieldName, yFieldName]].mean()
        myDf = pd.DataFrame({xFieldName: mySeries[xFieldName], yFieldName: mySeries[yFieldName]})
    elif DAY_OF_WEEK in globalOptionsDict:
        mySeries = myDf.groupby(DAY_OF_WEEK)[[xFieldName, yFieldName]].mean()
        myDf = pd.DataFrame({xFieldName: mySeries[xFieldName], yFieldName: mySeries[yFieldName]})
    

    xData = myDf.iloc[:, myDf.columns.get_loc(xFieldName)].values.reshape(-1, 1)
    yData = myDf.iloc[:, myDf.columns.get_loc(yFieldName)].values.reshape(-1, 1)
    plt.xlabel(xFieldName)
    plt.ylabel(yFieldName)
    ax = plt.scatter(xData, yData).axes
    rSquared = 0
    if not scatter:
        linearRegresser = LinearRegression()
        linearRegresser.fit(xData, yData)
        Y_pred = linearRegresser.predict(xData)
        rSquared = linearRegresser.score(xData,yData)
        plt.plot(xData, Y_pred, color='red')
        currentGraphName = xFieldName + yFieldName + graphTitle + "Regression"

        # Print R Squared value in top right
        # From: https://stackoverflow.com/questions/25771752/python-position-text-box-fixed-in-corner-and-correctly-aligned
        ax.annotate("rSqr = %f" % rSquared, xy=(1, 1), xytext=(-15, -15), fontsize=10,
        xycoords='axes fraction', textcoords='offset points',
        bbox=dict(facecolor='white', alpha=0.8),
        horizontalalignment='right', verticalalignment='top')
    else:
        currentGraphName = xFieldName + yFieldName + "Scatter"
    plt.title(xFieldName + " " + yFieldName + " Regression")
    graphPath = os.environ.get(GRAPH_PATH_ENV_VARIABLE)
    if graphPath == None:
        print("ENVIRONMENTAL VARIABLE %s NOT SET. ABORTING SAVE." % GRAPH_PATH_ENV_VARIABLE)
    else:
        fullPath = graphPath + filename
        print("Saving to path %s" % fullPath)
        plt.savefig(fullPath)
    plt.clf()
    plt.cla()
    return currentGraphName

def slrValidateOptions(optionsList):
    groupOptions = [MONTH_FIELD, WEEK_FIELD, DAY_OF_WEEK]
    for option in optionsList:
        if option in groupOptions:
            raise(Exception("SLR Options Wrong"))
    return True

def histogram(df, fieldName, optionsDict, fileSaveName):
    saveLocation = os.environ.get('GRAPH_SAVE_LOCATION')
    if saveLocation == None:
        # print("Saving to globalConstants save location %s" % GRAPH_PATH_FROM_SRC)
        print("SAVE LOCATION ENVIRONEMNTAL VARIABLE NOT SET. ABORTING FILE SAVE")
        return

    myDf = df[fieldName]
    myDf.plot(kind='hist')
    ax = myDf.plot.hist()
    nData = len(myDf)

    # Right align n string to top right
    # From: https://stackoverflow.com/questions/25771752/python-position-text-box-fixed-in-corner-and-correctly-aligned
    ax.annotate("n = %d" % nData, xy=(1, 1), xytext=(-15, -15), fontsize=10,
    xycoords='axes fraction', textcoords='offset points',
    bbox=dict(facecolor='white', alpha=0.8),
    horizontalalignment='right', verticalalignment='top')

    print("Saving to specified saveLocation %s" % saveLocation)
    print("CHANGE THIS, N ALWAWYS THE SAME")
    plt.title(fieldName)
    plt.savefig(saveLocation + fileSaveName)
    plt.cla()
    plt.clf()


def scatter(xDataFormat, yDataFormat, xOptionsDict, yOptionsDict, globalOptionsDict, originalDf, firstDate = None, lastDate = None):
    simpleLinearRegression(xDataFormat, yDataFormat, xOptionsDict, yOptionsDict, globalOptionsDict, originalDf, firstDate = None, lastDate = None, scatter = True)

def printStartDate(dataFormat, myDf):
    myDf = myDf.copy()
    myDf = myDf[myDf[dataFormat.finalName].notnull()]
    print(dataFormat.finalName, end = " ")
    print(myDf.iloc[0][DATE_FIELD], end = " ")
    print(myDf.iloc[0][dataFormat.finalName])

def sumDfs(oldTitle1, oldTitle2, dataFormat1, dataFormat2, newTitle, df):
    df = dataCleanup(df, {}, oldTitle1, dataFormat1)
    df = dataCleanup(df, {}, oldTitle2, dataFormat2)
    df[newTitle] = df.loc[:, oldTitle1].add(df.loc[:, oldTitle2])
    return df

def setDates(df):
    df[DATE_FIELD] = df[DATE_FIELD].apply(pd.to_datetime)
    df[MONTH_FIELD] = df[DATE_FIELD].apply(lambda x: (x.year, x.month))
    df[WEEK_FIELD] = df[DATE_FIELD].apply(lambda x: (x.year, x.weekofyear) if not (x.month == 1 and x.weekofyear == 52) else (x.year - 1, x.weekofyear))
    df[DAY_OF_WEEK] = df[DATE_FIELD].apply(pd.Timestamp.isoweekday)
    return df
