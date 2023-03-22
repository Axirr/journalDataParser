import src.plainTextDailyNotesParser as PlainText
from src.globalConstants import *
from sys import argv
import os

def mainReadPlaintext(isPublic):
    PlainText.main(isPublic)

if __name__ == "__main__":
    print("Using database %s" % os.getenv(DATABASE_NAME_ARG))
    isPublic = False
    if len(argv) > 1 and READ_PUBLIC_ONLY_ARG in argv:
        isPublic = True
    mainReadPlaintext(isPublic)