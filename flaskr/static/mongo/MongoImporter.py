import MongoUpdater
#import ParseTweetsRE
#import TweetCollect
import argparse
from pymongo import MongoClient
import json

# dbName collectionName tweetFile mongoUpdaterStartCutoff mongoUpdaterEndCutoff #filterWords
# MongoUpdater Format: Wed May 29 22:19:04
def main():
    args = setupCLI()
    dbName = args[0]
    collectionName = args[1]
    tweetFile = args[2]
    mongoUpdaterStartCutoff = args[3]
    mongoUpdaterEndCutoff = args[4]
    server = args[5]
    #filterWords = args[5]

    collection = connectToMongo(dbName, collectionName, server)
    importTweets(tweetFile, collection)

    MongoUpdater.dbName = dbName
    MongoUpdater.collectionName = collectionName
    MongoUpdater.startCutoff = mongoUpdaterStartCutoff
    MongoUpdater.endCutoff = mongoUpdaterEndCutoff


def importTweets(tweetFileName, collection):
    for line in open(tweetFileName):
        if line.strip():
            tweet = json.loads(line)
            collection.insert_one(tweet)


def connectToMongo(dbName, collectionName, server):
    if server == "local":
        client = MongoClient('localhost', 27017)
    else:
        client = MongoClient("mongodb://administrator:mongodb-VM3@10.2.3.7")

    db = client[dbName]
    collection = db[collectionName]
    return collection


def setupCLI():
    parser = argparse.ArgumentParser()
    parser.add_argument('databaseName', type=str)
    parser.add_argument('collectionName', type=str)
    parser.add_argument("tweetFile", type=str)
    parser.add_argument("mongoUpdaterStartCutoff", type=str)
    parser.add_argument("mongoUpdaterEndCutoff", type=str)
    #parser.add_argument('filterWords', type=str)
    parser.add_argument("--server", type=str, help="l=local (default), v=VirtualMachine-3")
    args = parser.parse_args()

    dbName = args.databaseName
    collectionName = args.collectionName
    tweetFile = args.tweetFile
    mongoUpdaterStartCutoff = args.mongoUpdaterStartCutoff
    mongoUpdaterEndCutoff = args.mongoUpdaterEndCutoff
    #filterWordArg = args.filterwords

    #if " OR " not in filterWordArg:
    #    filterList = [filterWordArg]
    #else:
    #    filterList = filterWordArg.split(" OR ")

    if args.server:
        if str.lower(args.server) == "l":
            server = "local"
        else:
            server = "vm3"
    else:
        server = "local"

    argsList = [dbName, collectionName, tweetFile, mongoUpdaterStartCutoff, mongoUpdaterEndCutoff, server]
    return argsList


if __name__ == '__main__':
    main()