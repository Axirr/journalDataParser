class DataFormat():
    def __init__(self, searchName, lineInstructions, separator, parseType, customRemovalList, nullType, finalName):
        # Used by parser to find relevant line to begin search
        self.searchName = searchName

        # Pattern used by parser to find lines after the start line
        self.lineInstructions = lineInstructions

        # Separator between field name and value
        self.separator = separator

        # Type of value
        self.parseType = parseType

        # List of patterns to remove from all instances from line
        self.customRemovalList = customRemovalList

        # Data field name in output file
        self.finalName = finalName

        # Data to search for in lines indented under the start line
        self.subDataFormats = []

        # Approach to filling in or removing null values
        self.nullType = nullType
    
    def addSubDataFormat(self, dataFormat):
        self.subDataFormats.append(dataFormat)