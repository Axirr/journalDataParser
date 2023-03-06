from src.globalConstants import UPDATE_ALL_SQL
from src.readCSVtoSQL import readCSVtoSQLMain
from sys import argv

def main(addOnly):
    readCSVtoSQLMain(addOnly)

if __name__ == "__main__":
    addOnly = True
    if len(argv) > 1 and UPDATE_ALL_SQL in argv:
        addOnly = False
    main(addOnly)