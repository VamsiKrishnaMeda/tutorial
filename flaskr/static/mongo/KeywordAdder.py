"""
    KeywordAdder
    Authors:        Shawn Huesman, Vamsi Krishna Meda
    Created on:     Oct 27, 2019
    Last Modified:  Apr 16, 2020
    Purpose:        Update MongoDb collection with Keywords in each tweet text

    Configuration:
    dbName collectionName filterWords --server
    tweet_db1 vaccines_5_16_2019 "Vaccines OR Immune" --server vm3

"""
from bson import json_util
from pymongo import MongoClient
import re
import argparse
import json


def main():
    """
    Sets Command Line argumets, finds Keywords in each tweet

    """
    args = setupCLI()
    collection = args[0]
    server = args[1]
    filterList = args[2]
    filterText = args[3]
	
    QUOTED_STRING_RE = re.compile(
        r"(text|expanded_url|display_url)\"((:\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])))|(:\"))?"
        + "(" + filterText + ")" + "[^a-zA-Z0-9_]", re.I)

    totalDocuments = collection.count_documents({})
    tweetCounter = 0
    for doc in collection.find({}):
        #1141468341623754758
        #1141467362757152768
        #1141459626917093377
        #1141458140917116929
        #1141461502161018882
        #1141462880228974592
        print("\r", end="")
        print("Current # of MongoDB tweet documents read out of", totalDocuments, ":", tweetCounter, end="")
        tweetCounter = tweetCounter + 1

        # Removed the 'if' condition since '$addToSet' ensures no duplication and to allow changes by new code
        #if "filter_words" not in doc:

        # MongoDB docs are converted into the same format as json collected tweets from Tweepy so they can be searched by regex
        matches = re.findall(QUOTED_STRING_RE, str(json.dumps(doc, default=json_util.default, separators=(',', ':'))))

        if matches:
            # Adding all the matched keywords to a list
            matchesFound = []
            for filterWord in filterList:
                if str("'" + filterWord.lower() + "'") in str(matches).lower() \
                        or str(" " + filterWord.lower() + " ") in str(matches).lower():
                    matchesFound.append(filterWord)
            # Updating document only once using matched keyword list once
            # Previous version didn't capture all keywords for some reason
            collection.update_one(
                {"id": doc["id"]},
                {"$addToSet": {"filter_words": {"$each" : matchesFound}}}
            )


def connectToMongo(dbName, collectionName, server):
    """
    Handles connecting to MongoDb and returns the collection

    Parameters
    ----------
    dbName: str
        Name of the Database

    collectionName: str
        Name of the Collection

    server: str
        Name of the server (localhost or VM3)

    Returns
    -------
    MongoDb collection

    """
    if server == "local":
        client = MongoClient('localhost', 27017)
    else:
        client = MongoClient("mongodb://administrator:mongodb-VM3@10.2.3.7")

    db = client[dbName]
    collection = db[collectionName]
    return collection


def setupCLI():
    """
    Handles the command line arguments for running the code, making optional date arguments easier and
    cleaner to handle

    Returns
    -------
    List of formatted Command Line arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('databaseName', type=str)
    parser.add_argument('collectionName', type=str)
    parser.add_argument('filterwords', type=str)
    parser.add_argument("--server", type=str, help="l=local, v=VirtualMachine-3 (default)")
    args = parser.parse_args()
    dbName = args.databaseName
    collectionName = args.collectionName
    filterWordArg = args.filterwords

    if args.server:
        if str.lower(args.server) == "l":
            server = "local"
        else:
            server = "vm3"
    else:
        server = "vm3"

    collection = connectToMongo(dbName, collectionName, server)

    if " OR " not in filterWordArg:
        filterList = [filterWordArg]
        filterText = filterWordArg
    else:
        filterList = filterWordArg.split(" OR ")
        filterText = filterWordArg.replace(" OR ", "|")

    argList = [collection, server, filterList, filterText]
    return argList


if __name__ == "__main__":
    main()