######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VER INFO IN MAIN.PY 13/2/2018  ######

'''All the functions for Colonel Sawyer relating to the Discord integration'''

import json
import re
import os
from datetime import datetime
from globalvar import redditposts, reddit, redditevents
from discord import post_discord

#############################################
#### REDDIT POST MAKER                   ####
#############################################

def post_reddit(post="aar", eventtitle=""):

    '''This code formats and makes the reddit posts'''

    global redditposts
    for item in redditposts:
        if((item["postname"] == post) and ((datetime.strptime(item["nextpost"], '%Y-%m-%d %H:%M:%S')) < datetime.now())):
            redditposts.remove(item)

            # MAKE POST ON SUBREDDIT
            subreddit = reddit.subreddit(item["subreddit"])
            subreddit.submit(title=item["posttitle"]+eventtitle, selftext=item["postbody"])
            subreddit = reddit.subreddit('combinedarms')

            # CALCULATE NEXT POST TIME
            calcpost = datetime.strptime(item["nextpost"], '%Y-%m-%d %H:%M:%S')
            if "s" in item["postinterval"]:
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(second=calcpost.second+tempval)
            elif "h" in item["postinterval"]:
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(hour=calcpost.hour+tempval)
            elif "d" in item["postinterval"]:
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(day=calcpost.day+tempval)
            elif "m" in item["postinterval"]:
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(month=calcpost.month+tempval)
            elif "y" in item["postinterval"]:
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(year=calcpost.year+tempval)
            else:
                item["nextpost"] = calcpost.replace(second=calcpost.second()+1)

            item["nextpost"] = str(item["nextpost"])
            redditposts.append(item)

            # RELOADS POSTS DICTIONARY
            with open(os.getcwd()+'/config/redditposts.json', 'w') as outfile:
                json.dump(redditposts, outfile, indent=4)
            with open(os.getcwd()+'/config/redditposts.json') as json_file:
                redditposts = json.load(json_file)

#############################################
#### PROCESSES REDDIT EVENT POSTS        ####
#############################################

def eventposthandle(submission):

    '''Ingests the event posts as they are made on the subreddit'''

    eventstring = submission.title
    if((eventstring.count("|") != 2) or ("]" not in eventstring) or ("[" not in eventstring)):
        return
    postdictionary = {"original":"", "game":"", "event-title":"", "event-desc":"", "event-datetime":"", "event-host":"", "event-url":"", "reddit-id":""}

    ##### EATS STRINGS #####

    postdictionary["original"] = eventstring
    postdictionary["reddit-id"] = submission.shortlink
    postdictionary["event-host"] = str(submission.author)
    postdictionary["event-url"] = submission.url

    # Identifies game string & enters it
    game = eventstring.split("]")[:1]
    game = (str(game)[4:(len(str(game))-2)])
    postdictionary["game"] = game

    # Identifies and isolates metadata strings

    digester = eventstring.split("|")
    blanklist = []

    stripvalue = len(game)+3
    digester[0] = digester[0][stripvalue:]
    for unit in digester:
        unit = unit.strip()
        blanklist.append(unit)

    postdictionary["event-title"] = blanklist[0]
    postdictionary["event-desc"] = blanklist[1]

    # Parsing the date into something useful
    blanklist[2] = blanklist[2].replace(" UTC", "")
    try:
        blanklist[2] = datetime.strptime(blanklist[2], '%a %b%d %H%M')
        # Apply correct year if someone schedules an event early in the next year
        blanklist[2] = blanklist[2].replace(year=datetime.now().year)
        if blanklist[2].month < datetime.today().month:
            blanklist[2] = blanklist[2].replace(year=(datetime.now().year+1))
        postdictionary["event-datetime"] = str(blanklist[2])
    except:
        postdictionary["event-datetime"] = "2000-04-01 19:00:00"
    nowdate = datetime.now()
    postdate = datetime.strptime(postdictionary["event-datetime"], '%Y-%m-%d %H:%M:%S')
    postdate = postdate.replace(hour=postdate.hour)
    if (postdictionary not in redditevents) and (postdate > nowdate):
        redditevents.append(postdictionary)
        post_discord("events", postdictionary["event-url"])
    with open(os.getcwd()+'/config/redditevents.json', 'w') as outfile:
        json.dump(redditevents, outfile, indent=4)
