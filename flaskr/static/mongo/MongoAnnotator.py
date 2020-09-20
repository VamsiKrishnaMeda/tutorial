"""
    MongoAnnotator
    Authors: Alina Campan, Shawn Huesman
    Created: June 10 2019
    Last Updated: October 3 2019

    Description: Allows for annotation of tweets organized by keyword.

    Shows: full tweet text, full quote text (if applicable), keywords found in tweet,
    tweet type (Tweet, Quote, Retweet, Reply), Tweet ID, and tweet hyperlink

    datbaseName collectionName filterwords user --server --maxTweets

"""

from pymongo import MongoClient
import argparse
import textwrap

def main():
    args = setupCLI()
    collection = args[0]
    user = args[1]
    filterList = args[2]
    maxTweets = args[3]

    filterWordGroups = createFilterWordGroups(filterList, createTweetList(collection, filterList), maxTweets)

    for filterWord in filterList:
        annotationAmount = filterWordGroups[filterWord + "AnnotationAmount"]
        for tweetID in filterWordGroups[filterWord]:
            #print(filterWord + " " + str(tweetID) + " " + str(annotationAmount))

            # break so no more than required amount of tweets are annotated
            if annotationAmount == 0:
                break

            displayTweetInformation(tweetID, filterWordGroups, filterWord, collection, user)


def displayTweetInformation(tweetID, filterWordGroups, filterWord, collection, user):
    tweet = filterWordGroups[tweetID]
    annotationFound = findIfTweetAnnotated(tweetID, collection)

    if annotationFound:
        print("Annotation for tweet #" + str(tweetID) + " for group " + filterWord + " found")
    else:
        printTweetInformation(tweet)
        annotateTweet(tweet, collection, user)
        filterWordGroups[filterWord + "AnnotationAmount"] -= 1


def annotateTweet(tweet, collection, user):
    print(" ")
    while True:
        annotation = input("r for relevant, i for irrelevant:")
        if annotation.lower() == 'r':
            collection.update_one(
                {"id": tweet.id},
                {"$set": {"annotation_" + str(user): 'r'}}

            )
            break
        elif annotation.lower() == "i":
            collection.update_one(
                {"id": tweet.id},
                {"$set": {"annotation_" + str(user): 'i'}}

            )
            break
        else:
            print("Incorrect response. r for relevant, i for irrelevant")
            continue


def printTweetInformation(tweet):
    wordWrapAmount = 155
    print("")
    print("~Tweet Type: " + str(tweet.type))

    if "Quote" in tweet.type:
        print("Quote Text:")
        print(textwrap.fill(str(tweet.quote), wordWrapAmount))
        print("")

    print("Tweet Text:")
    print(textwrap.fill(str(tweet.text), wordWrapAmount))
    print("")
    print("~Tweet URL: " + "https://twitter.com/statuses/" + str(tweet.id))


def findIfTweetAnnotated(tweetID, collection):
    tweetAnnotated = False
    user_nums = [1,2,3,4]
    for tweetDoc in collection.find({"id" : tweetID}):
        for num in user_nums:
            if "annotation_" + str(num) in tweetDoc:
                if tweetDoc["annotation_" + str(num)]:
                    tweetAnnotated = True
                    break
    return tweetAnnotated


def createFilterWordGroups(filterList, tweetList, maxTweets):
    filterWordGroups = {}
    filterCounter = 0

    # Initialize
    for filterWord in filterList:
        filterWordGroups[filterWord] = []
        filterWordGroups[filterWord + "Count"] = 0
        filterWordGroups[filterWord + "AnnotationAmount"] = 0

    for filterWord in filterList:
        # Count
        for tweet in tweetList:
            if tweet.keywords:
                if str.lower(filterWord) in tweet.keywords:
                    filterWordGroups[filterWord].append(tweet.id)
                    filterCounter += 1
            filterWordGroups[tweet.id] = tweet
        filterWordGroups[filterWord + "Count"] = filterCounter
        filterCounter = 0

        annotationAmount = maxTweets
        if len(filterWordGroups[filterWord]) < maxTweets:
            annotationAmount = len(filterWordGroups[filterWord])

        filterWordGroups[filterWord + "AnnotationAmount"] = annotationAmount
    return filterWordGroups


def createTweetList(collection, filterList):
    totalDocuments = collection.count_documents({})
    tweetCounter = 1
    tweetList = []
    for doc in collection.find({}):
        tweetID = doc["id"]
        tweetText = findTweetText(doc)
        tweetQuote = findTweetQuote(doc)
        tweetKeywords = findTweetKeywords(doc)
        tweetType = findTweetType(doc)
        tweetLink = "https://twitter.com/statuses/" + str(tweetID)
        tweetAnnotationGroup = findTweetAnnotationGroup(filterList, tweetKeywords)
        print("\r", end="")
        print("Current # of MongoDB tweet documents read out of", totalDocuments, ":", tweetCounter, end="")
        tweetCounter += 1

        tweet = make_tweet(tweetID, tweetText, tweetQuote, tweetKeywords, tweetType, tweetLink, tweetAnnotationGroup)
        tweetList.append(tweet)
    print("")
    return tweetList


def findTweetAnnotationGroup(filterList, keywords):
    for filterWord in filterList:
        if keywords:
            if str.lower(filterWord) in keywords:
                return filterWord


def findTweetKeywords(doc):
    tweetKeywords = []
    if "filter_words" in doc:
        for keyword in doc["filter_words"]:
            tweetKeywords.append(str.lower(keyword))
    else:
        tweetKeywords = None
    return tweetKeywords


def findTweetQuote(doc):
    if str(doc["is_quote_status"]) == "True":
        if "quoted_status" in doc:
            if "extended_tweet" in doc["quoted_status"]:
                tweetQuoteText = doc["quoted_status"]["extended_tweet"]["full_text"]
            else:
                tweetQuoteText = doc["quoted_status"]["text"]
        else:
            tweetQuoteText = None
    else:
        tweetQuoteText = None
    return tweetQuoteText


def findTweetType(doc):
    tweetType = "Tweet"
    if str(doc["is_quote_status"]) == "True":
        tweetType = tweetType + ", Quote"
    if "retweeted_status" in doc:
        tweetType = tweetType + ", Retweet"
    if str(doc["in_reply_to_status_id"]) != "None":
        tweetType = tweetType + ", Reply"
    return tweetType


def findTweetText(doc):
    if "retweeted_status" in doc:
        if "extended_tweet" in doc["retweeted_status"]:
            tweetText = doc["retweeted_status"]["extended_tweet"]["full_text"]
        else:
            tweetText = doc["retweeted_status"]["text"]
    elif "extended_tweet" in doc:
        tweetText = doc["extended_tweet"]["full_text"]
    else:
        tweetText = doc["text"]
    return tweetText


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
    parser.add_argument('filterwords', type=str)
    parser.add_argument("user", type=str)
    parser.add_argument("--server", type=str, help="l=local, v=VirtualMachine-3 (default)")
    parser.add_argument("--maxTweets", type=int, help="total amount of tweets to annotate for each word")
    args = parser.parse_args()
    dbName = args.databaseName
    collectionName = args.collectionName
    filterWordArg = args.filterwords

    if str.lower(args.user) == "alina":
        user = 1
    elif str.lower(args.user) == "celine":
        user = 2
    elif str.lower(args.user) == "marius":
        user = 3
    elif str.lower(args.user) == "shawn":
        user = 4
    else:
        user = None

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
    else:
        filterList = filterWordArg.split(" OR ")

    if args.maxTweets:
        maxTweets = args.maxTweets
    else:
        maxTweets = 50

    argList = [collection, user, filterList, maxTweets]
    return argList


def make_tweet(tweetID, tweetText, tweetQuote, tweetKeywords, tweetType, tweetLink, tweetAnnotationGroup):
    tweet = Tweet(tweetID, tweetText, tweetQuote, tweetKeywords, tweetType, tweetLink, tweetAnnotationGroup)
    return tweet


class Tweet:
    def __init__(self, tweetID, tweetText, tweetQuote, tweetKeywords, tweetType, tweetLink, tweetAnnotationGroup):
        self.id = tweetID
        self.text = tweetText
        self.quote = tweetQuote
        self.keywords = tweetKeywords
        self.type = tweetType
        self.link = tweetLink
        self.group = tweetAnnotationGroup


if __name__ == '__main__':
    main()