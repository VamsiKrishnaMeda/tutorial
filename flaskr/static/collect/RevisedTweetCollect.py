"""
Author:         Tobel Atnafu, Parker Kain, Vamsi Krishna Meda
Created On:     Feb 17, 2020
Last Modified:  Feb 20, 2020
Purpose:        Collect Tweets using tweepy
Usage:          python TweetCollect.py "FIFA OR Ronaldo" rawTweetsFile.txt summaryFile.txt KeySet1.txt 2 17 43
Usage:          python TweetCollect.py "FIFA OR Ronaldo" rawTweetsFile.txt summaryFile.txt KeySet1.txt 2 17 43 --date 02 10 2019

"""

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import datetime
from datetime import timedelta
import time
import argparse
import json
import os
import math

# -------------------------------------------------------------------------


def setupCLI():
    """
    Handles the command line arguments for running the code, making optional date arguments easier and
    cleaner to handle

    Returns
    -------
    List of arguments
    """
    # Deifne CLI
    CLI = argparse.ArgumentParser()

    # Add and name arguments

    # Mandatory arguments
    CLI.add_argument(
        "filter",
        type=str)
    CLI.add_argument(
        "output_file",
        type=str)
    CLI.add_argument(
        "summary_file",
        type=str)
    CLI.add_argument(
        "key_set_file",
        type=str)
    CLI.add_argument(
        "duration",
        type=int)
    CLI.add_argument(
        "startTime",
        nargs=2,
        type=int)

    # Optional arguments
    CLI.add_argument(
        "--date",
        nargs=3,
        type=int,
        default=[datetime.datetime.today().month,
                 datetime.datetime.today().day,
                 datetime.datetime.today().year]  # default if nothing is provided
    )

    return(CLI.parse_args())

# -------------------------------------------------------------------------------


def datetime_from_local_to_utc(local_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(
        now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return local_datetime - offset

# -------------------------------------------------------------------------------

# This is a basic listener that just prints received tweets to stdout.


class StdOutListener(StreamListener):
    def __init__(self):
        """
        This listener does the heavy lifting of reacting to incoming tweets.
        Also handles exiting of reading. 

        Parameters
        ----------
        StreamListener: Listener connection to twitter

        """
        # Set defaults
        self.onDataTriggered = False
        self.btime = time.time()
        self.counter = 0
        self.ids = []
        self.lastTime = None

    def on_data(self, data):
        """
        Handles reading of incoming tweets. Opens the specified text 
        file and writes information about tweets to it

        Parameters:
        data: Incoming tweet
        
        """
        # Set when listening will stop
        endTime = startDate + timedelta(minutes=duration)

        # prints the first time for the first data encountered
        if (self.onDataTriggered is False):
            self.onDataTriggered = True
            print("on_data time : " + str(datetime.datetime.now().hour) + ":" +
                  str(datetime.datetime.now().minute) + ":" + str(datetime.datetime.now().second))
            sumFile = open(summaryFile, "a+", encoding="utf-8")
            sumFile.write(
                'firstData,' + str(datetime_from_local_to_utc(datetime.datetime.now())) + '\n\n')
            sumFile.close()

        # Changed so that file name includes date and hour
        tweet = json.loads(data)
        timestamp_ms = 785007057000
        if 'created_at' in tweet:
            timestamp_ms = int(tweet['timestamp_ms'])
        elif 'limit' in tweet:
            timestamp_ms = int(tweet['limit']['timestamp_ms'])
        time = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0)
        hour = time.hour
        if hour < 10:
            hour = '0' + str(hour)
        else:
            hour = str(hour)
        with open(outputFile + ' ' + str(datetime.datetime.date(time)) + ' ' + hour + '.txt', 'a+', encoding='utf-8') as file:
            file.write(str(data))

        #json_line = json.loads(data)
        # if datetime.datetime.now() < endTime:
        #    self.lastTime = json_line['created_at']

        # End listening ---
        if datetime.datetime.now() >= endTime:
            with open(summaryFile, "a+", encoding="utf-8") as sumFile:
                sumFile.write('Last Data: ' + str(self.lastTime) + '\n')
            print("Finished Stream at : " + str(datetime.datetime.now().hour) + ":" +
                  str(datetime.datetime.now().minute) + ":" + str(datetime.datetime.now().second))
            exit()

        return True

    def on_error(self, status):
        """
        Handles any errors

        Parameters:
        status: Status of the error

        """
        print(status)

# ------------------------------------------------------------------------------


if __name__ == '__main__':

    # This handles Twitter authetification and the connection to Twitter Streaming API
    #print("Main starting time : " + str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":" + str(datetime.datetime.now().second))
    start = False
    stop = True
    l = 0

    # Set up reading of command line arguments
    args = setupCLI()

    searchFilter = args.filter
    outputFile = 'C:\\Users\\bncmo\\Downloads\\' + str(args.output_file).split('.')[0]
    times = datetime.datetime.now()
    hour = str(times.hour)
    summaryFile = 'C:\\Users\\bncmo\\Downloads\\' + args.summary_file
    keyFile = args.key_set_file
    duration = int(args.duration) + 1  # Run one minute past defined endtime

    # Handle filter, if multiple parameters were passed
    if searchFilter != "":
        searchFilter = searchFilter.split(' OR ')
    print('This is the current search filter: ', searchFilter)

    # Handle start time variables
    startHour = args.startTime[0]
    startMin = args.startTime[1]  # Run one minute before defined start time
    startMonth = args.date[0]
    startDay = args.date[1]
    startYear = args.date[2]

    startDate = datetime.datetime(
        startYear, startMonth, startDay, startHour, startMin)

    """if os.path.exists(outputFile):
        os.remove(outputFile)
    if os.path.exists(summaryFile):
        os.remove(summaryFile)
    try:
        os.mkdir('Output')
    except:
        print('Output folder already exists')"""

    # Read from key file to set variables for the user credentials to access Twitter API
    file = open(keyFile, "r")
    line = file.readline()
    ACCESS_TOKEN = line.split("= ", 1)[1].split("\n")[0]
    line = file.readline()
    ACCESS_SECRET = line.split("= ", 1)[1].split("\n")[0]
    line = file.readline()
    CONSUMER_KEY = line.split("= ", 1)[1].split("\n")[0]
    line = file.readline()
    CONSUMER_SECRET = line.split("= ", 1)[1].split("\n")[0]
    # print(ACCESS_TOKEN)
    # print(ACCESS_SECRET)
    # print(CONSUMER_KEY)
    # print(CONSUMER_SECRET)

    print('\nCollection will begin at ...', startDate)
    print('The time is currently ...', datetime.datetime.now())
    print('Collection will continue for', args.duration, 'minutes')
    print('----------------------------------------------\n')

    sumFile = open(summaryFile, "a+", encoding="utf-8")
    sumFile.write('Variables,' + 'Values' + '\n')
    sumFile.write(
        'startDate,' + str(datetime_from_local_to_utc(startDate)) + '\n')
    sumFile.write('endDate,' + str(datetime_from_local_to_utc(startDate) +
                                   timedelta(minutes=duration - 1)) + '\n')
    sumFile.close()

    while stop:
        if(datetime.datetime.now() >= (startDate + timedelta(minutes=-1))):
            start = True
            stop = False
        else:
            print('sleeping .....')
            time.sleep(30)

    if(start):
        # record when listener starts
        #print("Listener time : " + str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":" + str(datetime.datetime.now().second))
        l = StdOutListener()

    # Start up Stream
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    stream = Stream(auth, l)

    # Start up listener
    # This line filter Twitter Streams to capture data by the keywords: ex('python', 'javascript', 'ruby')
    if (searchFilter == ""):
        print("\nStarting stream")
        stream.sample()
    else:
        print("\nStarting stream")
        stream.filter(track=searchFilter, is_async=True)

 # USE:
 # python TweetCollect.py "FIFA Ronaldo" rawTweetsFile.txt summaryFile.txt KeySet1.txt 2 17 43
 # above will run for 2 minutes beginning at 5:43 PM
 # OR
 # python TweetCollect.py "FIFA Ronaldo" rawTweetsFile.txt summaryFile.txt KeySet1.txt 2 17 43 --date 02 10 2019
 # multiple search term example:
 # python TweetCollect.py "dogs OR cats" rawTweetsFile.txt summaryFile.txt KeySet1.txt 2 17 43