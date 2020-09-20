"""
Author:         Vamsi Krishna Meda
Created On:     Apr 09, 2020
Last Modified:  Apr 18, 2020
Purpose:        Run TweetProcessing.py for each data file
Usage:          python RunTweetProcessing.py

"""

from os import listdir
from os.path import isfile, join
import subprocess
import time

path = 'Output/Coronavirus/'
summaryFile = join(path, 'Summary.txt')
#List of data files in the data collection folder
Files = [join(path, fileName) for fileName in listdir(path) if (isfile(join(path, fileName)) and '-' in fileName)]
counter = 0

for file in Files:
    process = subprocess.Popen(['python', 'Visualization/PyCode/TweetProcessing.py', file, summaryFile, '60', '60', '18', '00', '--date', '03', '01', '2020'], shell=True)
    # Wait till the process if finished 
    # Otherwise it will spawn a new process for all the files and overload the computer
    process.wait()
    counter += 1
    print('\r', end='')
    print('# of files processed out of', len(Files), ':', counter, end='')