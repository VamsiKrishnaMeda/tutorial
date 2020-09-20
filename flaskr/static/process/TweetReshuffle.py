"""
Author:         Vamsi Krishna Meda
Created On:     Jun 21, 2020
Purpose:        Reshuffles the tweets based on timestamp
Usage:          python TweetReshuffle.py

"""


import json
from os import listdir
from os.path import isfile, join
from datetime import datetime


if __name__ == '__main__':
    candidates = ['Biden', 'Bloomberg', 'Buttigieg', 'Klobuchar', 'Sanders', 'Warren']
    for candidate in candidates:
        path = 'Output/Election/Data/' + candidate + '/'
        outputFile = 'Output/Election/Reshuffled/' + candidate + '/' + candidate +'Tweets'
        Files = [join(path, filename) for filename in listdir(path) if isfile(join(path, filename)) and '-' in filename]
        count = 0
        start = datetime.now()

        for filename in Files:
            with open(filename, 'r') as file:
                for line in file:
                    if line.split():
                        tweet = json.loads(line)
                        timestamp_ms = 785007057000
                        if 'created_at' in tweet:
                            timestamp_ms = int(tweet['timestamp_ms'])
                        elif 'limit' in tweet:
                            timestamp_ms = int(tweet['limit']['timestamp_ms'])
                        time = datetime.fromtimestamp(timestamp_ms / 1000.0)
                        hour = time.hour
                        if hour < 10:
                            hour = '0' + str(hour)
                        else:
                            hour = str(hour)
                        with open(outputFile + ' ' + str(datetime.date(time)) + ' ' + hour + '.txt', 'a+', encoding='utf-8') as file:
                            file.write(str(tweet) + '\n' + '\n')
            count += 1
            print('\r', end="")
            print('# of files processed out of ' + str(len(Files)) + ': ' + str(count), end="")
    
    end = datetime.now()
    diff = end - start
    time = divmod(diff.total_seconds(), 60)
    print('\n' + str(time[0]) + ' minutes and ' + str(time[1]) + ' seconds')