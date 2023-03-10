import pandas as pd
from src.globalConstants import *
from privateSrc.myGraphCalls import setDates
import sqlalchemy as sqla
import os
from sqlalchemy.orm import Session
from src.DailyData import Base, Daily_Data
from sys import argv
from time import sleep

    

def readCSVtoSQLMain(addOnly):
    oldDf = pd.read_csv(HTML_PUBLIC_OUTPUT_FILE, parse_dates=True)
    newDf = pd.read_csv(PLAINTEXT_PUBLIC_OUTPUT_FILE, parse_dates=True)

    if addOnly:
        print("Only adding data that doesn't already exist")
    else:
        print("Trying to insert all data")
    sleep(1)


    pd.set_option('display.max_rows', None)

    df = pd.concat([oldDf, newDf], axis=0,ignore_index=True)

    df = setDates(df)

    url = os.environ.get('SQL_ALCHEMY_DB_INFO')
    if (url is None):
        print("Database info not set")
        exit()
    engine = sqla.create_engine(url, echo = True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for _, item in df.iterrows():
            myDate = item.date.to_pydatetime().date()
            if addOnly:
                myDateString = myDate.strftime("%Y-%m-%d")
                dateExists = session.query(Daily_Data.date).filter_by(date=myDateString).first() is not None
                if dateExists:
                    print("%s already exists" % myDateString)
                    continue

            myProgrammingMinutes = item.programmingMinutes
            myTVminutes = item.TVminutes
            myInsomniaRating = item.insomniaRating
            myRecreationMinutes = item.recreationMinutes
            myGameMinutes = item.gameMinutes
            myProductiveMinutes = item.productiveMinutes
            myWalkingMinutes = item.walkingMinutes

            if pd.isnull(myProgrammingMinutes):  myProgrammingMinutes = 0
            if pd.isnull(myInsomniaRating):  myInsomniaRating = None
            if pd.isnull(myTVminutes):  myTVminutes = 0
            if pd.isnull(myRecreationMinutes):  myRecreationMinutes = 0
            if pd.isnull(myGameMinutes):  myGameMinutes = 0
            if pd.isnull(myProductiveMinutes):  myProductiveMinutes = 0
            if pd.isnull(myWalkingMinutes):  myWalkingMinutes = 0

            newDaily=Daily_Data(date=myDate, programmingMinutes=myProgrammingMinutes, insomniaRating=myInsomniaRating, TVminutes=myTVminutes, recreationMinutes=myRecreationMinutes, gameMinutes=myGameMinutes, productiveMinutes=myProductiveMinutes, walkingMinutes=myWalkingMinutes)
            print(newDaily)
            session.add(newDaily)
        session.commit()
    
    return

if __name__ == "__main__":
    print("Module file. Should not be run directly.")
    # addOnly = True
    # if len(argv) > 1 and UPDATE_ALL_SQL in argv:
    #     addOnly = False
    # readCSVtoSQLMain(addOnly)