'''
 Created on May 29, 2019
 Author: Shawn Huesman
'''
from pymongo import MongoClient
import sys
import datetime


#CLI arguments
dbName = sys.argv[1]
collectionName = sys.argv[2]
startCutoff = sys.argv[3]
endCutoff = sys.argv[4]
# Cutoffs should be typed in this format: day month day# hour:minute:second
# Example: Wed May 29 22:19:04

def main():
    #-------------------------------------------------------------------------
    #Connect to MongoDB and establish database & collection from CLI arguments
    client = MongoClient('localhost', 27017)
    db = client[dbName]
    collection = db[collectionName]



    deleteCounter = 0
    for doc in collection.find({}):

        #Information regarding created time of tweet in MongoDB
        createdAt = doc["created_at"]
        monthCreated = createdAt.split(" ")[1]
        dayCreated = createdAt.split(" ")[2]
        timeCreated = createdAt.split(" ")[3]

        hourCreated = int(timeCreated.split(":")[0])
        minuteCreated = int(timeCreated.split(":")[1])
        secondCreated = int(timeCreated.split(":")[2])

        # Information regarding created time of start cutoff
        startMonthCutoff = startCutoff.split(" ")[1]
        startDayCutoff = startCutoff.split(" ")[2]
        startTimeCutoff = startCutoff.split(" ")[3]

        startHourCutoff = int(startTimeCutoff.split(":")[0])
        startMinuteCutoff = int(startTimeCutoff.split(":")[1])
        startSecondCutoff = int(startTimeCutoff.split(":")[2])

        # Information regarding created time of end cutoff
        endMonthCutoff = endCutoff.split(" ")[1]
        endDayCutoff = endCutoff.split(" ")[2]
        endTimeCutoff = endCutoff.split(" ")[3]

        endHourCutoff = int(endTimeCutoff.split(":")[0])
        endMinuteCutoff = int(endTimeCutoff.split(":")[1])
        endSecondCutoff = int(endTimeCutoff.split(":")[2])


        def monthToInt(monthName):
            monthInt = 0
            if monthName.lower() == "jan":
                monthInt = 1
            elif monthName.lower() == "feb":
                monthInt = 2
            elif monthName.lower() == "mar":
                monthInt = 3
            elif monthName.lower() == "apr":
                monthInt = 4
            elif monthName.lower() == "may":
                monthInt = 5
            elif monthName.lower() == "jun":
                monthInt = 6
            elif monthName.lower() == "jul":
                monthInt = 7
            elif monthName.lower() == "aug":
                monthInt = 8
            elif monthName.lower() == "sep":
                monthInt = 9
            elif monthName.lower() == "oct":
                monthInt = 10
            elif monthName.lower() == "nov":
                monthInt = 11
            elif monthName.lower() == "dec":
                monthInt = 12
            else:
                monthInt = 0

            return monthInt


        #Creates a date from the tweet in MongoDB, start cutoff, and end cutoff
        year = 2019
        month = monthToInt(monthCreated)
        day = int(dayCreated)

        startMonth = monthToInt(startMonthCutoff)
        startDay = int(startDayCutoff)

        endMonth = monthToInt(startMonthCutoff)
        endDay = int(endDayCutoff)

        createdDate = datetime.datetime(year,month,day,hourCreated,minuteCreated,secondCreated)
        startCutoffDate = datetime.datetime(year,startMonth,startDay,startHourCutoff,startMinuteCutoff, startSecondCutoff)
        endCutoffDate = datetime.datetime(year,endMonth,endDay,endHourCutoff,endMinuteCutoff,endSecondCutoff)

        #deletes tweets before start cutoff time and after end cutoff time
        if createdDate < startCutoffDate:
            collection.delete_one({'_id': doc['_id']})
            deleteCounter = deleteCounter + 1

        elif createdDate > endCutoffDate:
            collection.delete_one({'_id': doc['_id']})
            deleteCounter = deleteCounter + 1


    #Output information about deleted tweets
    print("Times before", startCutoff, "and after", endCutoff, "were deleted.")
    print(deleteCounter,"MongoDB documents deleted")

if __name__ == "__main__":
    main()
