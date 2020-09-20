from os import listdir
from os.path import isfile, join
import subprocess
import time
import re

bidenPath = 'Output/Election/BidenSummary/'
bidenCompPath = 'Output/Election/BidenComparision/'

sandersPath = 'Output/Election/SandersSummary/'
sandersCompPath = 'Output/Election/SandersComparision/'

unfilteredPath = 'Output/Election/UnfilteredSummary/'

bidenFiles = [fileName for fileName in listdir(bidenPath) if (isfile(join(bidenPath, fileName)) and 'IDs' in fileName and '.pkl' in fileName)]
sandersFiles = [fileName for fileName in listdir(sandersPath) if (isfile(join(sandersPath, fileName)) and 'IDs' in fileName and '.pkl' in fileName)]
unfilteredFiles = [fileName for fileName in listdir(unfilteredPath) if (isfile(join(unfilteredPath, fileName)) and 'IDs' in fileName and '.pkl' in fileName)]

for fileIndex in range(len(bidenFiles)):
    #Obtaining Biden Comparision filenames
    # tokens = re.split(r'[\s.]', bidenFiles[fileIndex])
    # bidenComp = join(bidenCompPath, 'BidenComparision ' + tokens[1] + ' ' + tokens[2] + '.csv')

    #Obtaining Sanders Comparision filenames
    tokens = re.split(r'[\s.]', sandersFiles[fileIndex])
    sandersComp = join(sandersCompPath, 'SandersComparision ' + tokens[1] + ' ' + tokens[2] + '.csv')

    # Biden Comparision
    # process = subprocess.Popen(['python', 'Visualization/PyCode/TweetCreateSummary.py', join(unfilteredPath, unfilteredFiles[fileIndex]), join(bidenPath, bidenFiles[fileIndex]), bidenComp])
    # process.wait()

    # Sanders Comparision
    process = subprocess.Popen(['python', 'Visualization/PyCode/TweetCreateSummary.py', join(unfilteredPath, unfilteredFiles[fileIndex]), join(sandersPath, sandersFiles[fileIndex]), sandersComp])
    process.wait()

    print('\r', end="")
    print('# of Files processed out of ', len(sandersFiles), ':', fileIndex + 1, end="")

# python TweetCreateSummary.py "Output\Unfiltered\Summary\IDs_UnfilteredTweets 2020-03-02 0.pkl" "Output\Biden\Summary\IDs_BidenTweets 2020-03-02 0.pkl" "Output\BidenComparision\BidenComp.csv"