class DataFormat():
    def __init__(self, searchName, lineInstructions, separator, parseType, customRemovalList, finalName = ""):
        self.searchName = searchName
        self.lineInstructions = lineInstructions
        self.separator = separator
        self.parseType = parseType
        self.customRemovalList = customRemovalList
        if finalName == "":
            self.finalName = searchName
        else:
            self.finalName = finalName
        self.subDataFormats = []
    
    def addSubDataFormat(self, dataFormat):
        self.subDataFormats.append(dataFormat)
