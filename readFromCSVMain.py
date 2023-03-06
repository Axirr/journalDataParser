from src.globalConstants import ADD_SQL_ARG
from src.readCSVtoSQL import readCSVtoSQLMain
from sys import argv

def main(addOnly):
    readCSVtoSQLMain(addOnly)

if __name__ == "__main__":
    addOnly = True
    if len(argv) > 1 and ADD_SQL_ARG in argv:
        addOnly = False
    main(addOnly)