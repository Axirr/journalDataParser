DATE_FIELD = "date"
WEEK_FIELD = "Weekly"
MONTH_FIELD = "Monthly"
YEAR_FIELD = "Yearly"
DAY_OF_WEEK = "DayOfWeek"

NO_WEEKEND = "NoWeekend"
AVG_LINE = "AvgLine"
ROLLING_AVERAGE = "RollingAverage"
Y_MAX = "YMax"
Y_MIN = "YMin"

BAR_OPTION = "Bar"
BOX_PLOT = "BoxPlot"
MULTI_PLOT = "MultiPlot"

FIRST_DATE = "FirstDate"
LAST_DATE = "LastDate"
GRAPH_TYPES = [BAR_OPTION, BOX_PLOT]

# VISUALIZATION_OLD_INPUT_FILENAME = "htmlOutput.csv"
# VISUALIZATION_NEW_INPUT_FILENAME = "plaintextOutput.csv"

NULL_MEANS_MISSING = "NotNull"
NULL_IS_ZERO = "NullIsZero"
SHIFT = "Shift"
NORMALIZE = "Normalize"

PARSER_NULL_VALUE = "null"
PARSER_OUTPUT_FILENAME = "./outputData/htmlOutput.csv"
NEW_PARSER_OUTPUT_FILENAME = "./outputData/plaintextOutput.csv"
PARSER_INPUT_FILENAME = "../../../daily.nnex"

NEW_PARSER_INPUT_FILENAME =  "../../../../../dailyData/dailyDataDec2022Jan2023.txt"
PLAINTEXT_INPUT_FILES = [
    NEW_PARSER_INPUT_FILENAME,
    "../../../../../dailyData/dailyDataFeb2023.txt",
    "../../../../../dailyData/dailyDataMarch2023.txt",
    ]
# PLAINTEXT_INPUT_FILES = [NEW_PARSER_INPUT_FILENAME2]
EARLIEST_DATE_FOR_FILE = [
    "december 6, 2022",
    "february 1, 2023",
    "march 1, 2023",
    ]

PLAINTEXT_PUBLIC_OUTPUT_FILE = "./outputData/publicOutput.csv"
HTML_PUBLIC_OUTPUT_FILE = "./outputData/publicHtmlOutput.csv"
#GRAPH_PATH_FROM_SRC = "../graphs/"
GRAPH_PATH_ENV_VARIABLE = 'GRAPH_SAVE_LOCATION'

READ_PUBLIC_ONLY_ARG = "public"
USE_SQL_AS_DATA_SOURCE = "sqlSource"

ADD_SQL_ARG = "add"
