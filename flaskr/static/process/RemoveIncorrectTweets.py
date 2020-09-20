"""
Created on Fri Jul 27 15:25:30 2018
Modified on Thr Aug 10 13:25:30 2018 by Marius Truta
Modified on Sat May 4 8:25:30 2019 by Marius Truta
Modified on Tue May 30 12:25:30 2019 by Marius Truta
@author: Alina Campan & Marius Truta
This is for filtering words with sepcial characters in other languages, not the original TweetParse with RE !!!!
"""
import sys
import re
import json

rawTweetsFile = sys.argv[1]
filterWord = sys.argv[2]
# below regular expression matches text|url":"(any characters except " repeated; \" are allowed) filterWord note that filtered word should be preceded/followed
# by a non alphanumeric caracter (to avoid AntoGriezmann or PERISICCCC matching). :filterWord is treated separately \nRonaldo is also included by ([^a-zA-Z0-9_]|(\\n))
# i also need to include /u201c among others so in changed it to (\\[a-zA-Z0-9_]*))
#     QUOTED_STRING_RE = re.compile(r"(text|url)\"((:\"([^\"]|(\\\"))*[^a-zA-Z0-9_])|(:\"))" + filterWord + "[^a-zA-Z0-9_]", re.I)  - old
#    QUOTED_STRING_RE = re.compile(r"(text|url)\"((:\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[a-zA-Z0-9_]*)))|(:\"))" + filterWord + "[^a-zA-Z0-9_]", re.I) - old

# I had to allow only specfic special characters before the filtered word. they may or may not be present (?). I belive (:\") is extra, no harm though. re.I ignore cases for filter word.
#  QUOTED_STRING_RE = re.compile(r"(text|expanded_url|display_url)\"((:\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])|(\\u[0-9a-fA-F]{4})))|(:\"))?" + filterWord + "[^a-zA-Z0-9_]", re.I)

# This is to eliminate tweets that have special characters near words (such as m\u00fasica)

filterList = []
filterText = ""

if " OR " not in filterWord:
    filterText = filterWord
else:
    filterList = filterWord.split(" OR ")
    filterText = filterList[0]
    for aFilterWord in filterList:
        filterText = filterText + "|" + aFilterWord

QUOTED_STRING_RE = re.compile(
    r"(text|expanded_url|display_url)\"((:\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])))|(:\"))?" + "(" + filterText + ")" + "[^a-zA-Z0-9_]",
    re.I)

deleteCounter = 0
with open(rawTweetsFile, 'r') as json_tweets:
    for line in json_tweets:
        searchObj = QUOTED_STRING_RE.search(line)
        # print(type(json_tweets))
        if searchObj:
            line2 = line[searchObj.start():searchObj.end()]
            #print(json_tweets)
            deleteCounter = deleteCounter + 1
            print(line)


# python ParseTweetsRE.py testJsonSearch.txt ronaldo > filteredTweetsFile.txt
#python ParseTweetsRE.py "C:\Users\shawn\Desktop\Huesman_VaccinesMay29.txt" "Bird flu OR Chicken pox OR Chickenpox OR Cholera OR Cica OR Cika OR Diphtheria OR Diptheria OR Dtap OR Dtp OR Dtwp OR Encephalitis OR Flushot OR Globulin OR H1n1 OR H7n9 OR Haemophilus OR Hepa OR Hepatitis OR hepb OR Hpv OR Immune OR Immunization OR Immunizations OR Imune OR Imunization OR Lyme OR Measles OR Meningitis OR Meningococcal OR Mmr OR Mumps OR Papillomavirus OR Pertussis OR Pneumococcal OR Polio OR Rabies OR Rotavirus OR Rubella OR Shingles OR Sica OR Sika OR Smallpox OR Tdap OR Tetanus OR Tuberculosis OR Typhoid OR Vaccinate OR Vaccinated OR Vaccine OR Vaccines OR Vacine OR Vacines OR Varicella OR Whooping cough OR Yellow fever OR Zeca OR Zeeca OR Zeeka OR Zeka OR Zica OR Zika" > filteredTweetsFile.txt