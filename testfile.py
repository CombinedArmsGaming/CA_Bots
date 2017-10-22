import json
from datetime import datetime
import time
import requests
import praw

with open('botconfig.json') as data_file:    
    botparams = json.load(data_file)[0]
# with open('discordconfig.json') as data_file:
#     discordchannels = json.load(data_file)[0]
with open('redditposts.json') as json_file:  
    postsdictionary = json.load(json_file)
# Instantiate Reddit Bot
reddit = praw.Reddit(client_id=botparams["reddit-client-id"],
                     client_secret=botparams["reddit-client-secret"],
                     password=botparams["reddit-password"],
                     user_agent=botparams["reddit-agent"],
                     username=botparams["reddit-username"])
subreddit = reddit.subreddit('combinedarms')


jsondictionary=[]

# Discord HTTP header initialisation
headers = { "Authorization":botparams["discord-token"],
            "User-Agent":"myBotThing (http://some.url, v0.1)",
            "Content-Type":"application/json", }

# def post_discord(channel,message):
#     # Load message payload
#     payload =  json.dumps ( {"content":str(message)} )
#     # Make HTTP request using header and payload defined earlier.
#     r = requests.post('https://discordapp.com/api/channels/'+discordchannels[str(channel)]+'/messages', headers=headers, data=payload)
#     # Prepare error message and overwrite it if the request was successful.
#     print ("Returned error code: " + str(r.status_code))
#     if r.status_code == 200:
#         print "Posted to Discord"

# def get_discord(channel):
#     # Make HTTP request using header and payload defined earlier.
#     r = requests.get('https://discordapp.com/api/channels/'+discordchannels[str(channel)]+'/messages', headers=headers)
#     if r.status_code == 200:
#         print "Received from Discord"
#     with open('discordmessages.json', 'w') as outfile:  
#         json.dump(r.json(), outfile,indent=4)
#     return r.json()

def post_reddit(post="aar"):
    for item in postsdictionary:
        if((item["postname"] == post) or ((datetime.strptime(item["nextpost"],'%Y-%m-%d %H:%M:%S')) < datetime.now())):
            print "posting "+str(post)
            subreddit.submit(title=item["posttitle"], selftext=item["postbody"])
post_reddit("rtm")

#    teststring = "[A3] Operation Mute Claw | Joint SOF | SUN OCT22 1900 UTC"

# with open('testdata.txt') as testdatatext:
#     for line in testdatatext:

#         if((line.count("|")!=2) or ("]" not in line) or ("[" not in line)):
#             continue

#         teststring = str(line)
#         testdictionary = {"original":"","game":"","event-title":"","event-desc":"","event-datetime":"","event-host":"","event-url":"","reddit-id":""}
    
#         ##### EATS STRINGS #####
        
#         testdictionary["original"]=teststring
#         testdictionary["reddit-id"]="76tg04"
#         testdictionary["event-host"]="fictionalperson"
#         testdictionary["event-url"]="http://reddit.com/r/combinedarms/fakepost"
        
#         # Identifies game string & enters it
#         game = teststring.split("]")[:1]
#         game = (str(game)[3:(len(str(game))-2)])
#         testdictionary["game"] = game
        
#         # Identifies and isolates metadata strings
        
#         digester = teststring.split("|")
#         blanklist = []
        
#         stripvalue = len(game)+2
#         digester[0] = digester[0][stripvalue:]
#         for unit in digester:
#             unit = unit.strip()
#             blanklist.append(unit)
    
#         testdictionary["event-title"]=blanklist[0]
#         testdictionary["event-desc"]=blanklist[1]
    
#         # Parsing the date into something useful
#         blanklist[2] = blanklist[2].replace(" UTC","")
#         blanklist[2] = datetime.strptime(blanklist[2],'%a %b%d %H%M')
#         # Apply correct year if someone schedules an event early in the next year
#         blanklist[2] = blanklist[2].replace(year = datetime.now().year)
#         if(blanklist[2].month < datetime.today().month):
#             blanklist[2] = blanklist[2].replace(year = (datetime.now().year+1))
        
#         testdictionary["event-datetime"]=str(blanklist[2])
        
#         for unit in testdictionary:
#             print (unit + " " + testdictionary[str(unit)])

#         jsondictionary.append(testdictionary)

# json = get_discord("events")

# for item in json:
#     for post in jsondictionary:
#         if str(post["reddit-id"]) in str(item):
#             postdate = datetime.strptime(post["event-datetime"],'%Y-%m-%d %H:%M:%S')
#             postdate = postdate.replace(hour = postdate.hour+1)
#             nowdate = datetime.now()
#             if postdate < nowdate:
#                 print "this has already happened"
