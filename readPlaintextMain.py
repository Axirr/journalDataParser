import src.plainTextDailyNotesParser as PlainText
from src.globalConstants import READ_PUBLIC_ONLY_ARG
from sys import argv

def mainReadPlaintext(isPublic):
    PlainText.main(isPublic)

if __name__ == "__main__":
    isPublic = False
    if len(argv) > 1 and READ_PUBLIC_ONLY_ARG in argv:
        isPublic = True
    mainReadPlaintext(isPublic)