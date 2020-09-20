import re


# Function to determine if a tweet in json=text format (the parameter line) 
# contains a term (the parameter filterWord)

def searchTweetForWord(line, filterWord):

    #Marius - June 9, 2020: ( )? is added after : to all RE because json.loads adds a space after : 
    QUOTED_STRING_RE1 = re.compile(r"(text)\"((:( )?\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])|(\\u[0-9a-fA-F]{4})))|(:\"))?" + filterWord + r"([^a-zA-Z0-9_\\]|(\\[^u])|(\\u[^2])|(\\u2[^0])|(\\u20[^2])|(\\u202[^6]))", re.I)  
    QUOTED_STRING_RE2 = re.compile(r"(full_text|expanded_url|display_url)\"((:( )?\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])|(\\u[0-9a-fA-F]{4})))|(:\"))?" + filterWord + r"([^a-zA-Z0-9_])", re.I)

    # this is the pattern for RT - retweets, we have to ignore "RT @MONEY:" 
    QUOTED_STRING_RE_RT = re.compile("text\":( )?\"RT @" + filterWord + ":", re.I)
	
    # this is the pattern for \u2026
    QUOTED_STRING_RE_THREEPOINTS = re.compile(r"(text)\"((:( )?\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])|(\\u[0-9a-fA-F]{4})))|(:\"))?" + filterWord + r"(\\u2026)", re.I)
    QUOTED_STRING_RE_THREEPOINTS_FULL = re.compile(r"(full_text)\"((:( )?\"([^\"]|(\\\"))*([^a-zA-Z0-9_]|(\\[bfnrt\"])|(\\u[0-9a-fA-F]{4})))|(:\"))?" + filterWord, re.I)

    # this is the pattern for general RT, we need to ignore them in some cases
    QUOTED_STRING_RE_GENERAL_RT = re.compile(r":( )?\"RT @[a-zA-Z0-9_]*: ", re.I)

    searchObj_RT = QUOTED_STRING_RE_RT.search(line)
    line_new = line
    # second part is to check if the RT part is because of a retweet, not because of someone typing it like is a retweet.
    if searchObj_RT and ",\"retweeted_status\":( )?{\"created_at\":\"" in line_new:
        line_new = QUOTED_STRING_RE_RT.sub("text\":( )?\"RT @XXXAAAXXX:",line_new)

    searchObj1 = QUOTED_STRING_RE1.search(line_new)
    if searchObj1:      # filterWord found in text, filterWord\u2026 is excluded
        return True
    else:
        searchObj2 = QUOTED_STRING_RE2.search(line_new)
        if searchObj2:		# filterWord found in fulltext or url, filterWord\u2026 is not excluded		
            return True	
        else:				
            searchObj3 = QUOTED_STRING_RE_THREEPOINTS.search(line_new)
            if searchObj3: #filterWord\u2026 found in text (so far the tweet has not beed selected)		
                searchObj4 = QUOTED_STRING_RE_THREEPOINTS_FULL.search(line_new)
                if searchObj4: #filterWord found in full_text, it may be followed by anything incuding letters
                    str1 = "\"full_text\"" + searchObj3.group(2)+filterWord
                    # the retweet part is not repeated in full_text; and we need to take it out; however if someone rwote RT in the tweet we still need to check for RT existance (second part from if statement)
                    str2 = re.sub(r"text\":( )?\"RT @[a-zA-Z0-9_]*: ", "text\":\"", str1, re.I)
                    if (str2.lower() not in line_new.lower()) and (str1.lower() not in line_new.lower()):
                        return True
                else:
                    # the retweet part is not repeated in second text; and we need to take it out; see 1116593840989728769 as example
                    searchObj5 = QUOTED_STRING_RE_GENERAL_RT.search("\"text\"" + searchObj3.group(2) + filterWord, re.I)
                    str1 = "\"text\"" + searchObj3.group(2)+filterWord
                    # the retweet part is not repeated in second text; and we need to take it out
                    str2 = re.sub(r"text\":( )?\"RT @[a-zA-Z0-9_]*: ", "text\":\"", str1, re.I)
							
                    if searchObj5:
                        # only case excluded is when str2 changes and str2 is in line_new, then filterWord is the prefix of a longer word (otherwise it would have been found in searchObj1
                        if not ((str1 != str2) and (str2.lower() in line_new.lower())):  #the string without the RT part must repeat in a second text to exclude the tweet
                            return True
                        else:  #this is when the second txt has something like money\u2026 and this is a separator, see 1116717546202443776 
                            if line_new[line_new.lower().find(str2.lower())+len(str2)] == "\\":
                                return True	
                    else:
                        return True
    return False