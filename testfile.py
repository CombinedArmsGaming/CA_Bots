import json
from datetime import datetime
import time
import praw


with open('botconfig.json') as data_file:    
    botparams = json.load(data_file)[0]
    
jsondictionary = []
vaguestring = "[A3] Operation Mute Claw | Joint SOF | SUN OCT22 1900 UTC"

reddit = praw.Reddit(client_id=botparams["reddit-client-id"],
                     client_secret=botparams["reddit-client-secret"],
                     password=botparams["reddit-password"],
                     user_agent=botparams["reddit-agent"],
                     username=botparams["reddit-username"])
subreddit = reddit.subreddit('combinedarms')

with open('redditevents.json') as json_file:  
    jsondictionary = json.load(json_file)





#with open('testdata') as testdatatext:
#    for line in testdatatext:
for submission in subreddit.new(limit=1):
    print submission.title
    line = submission.title
    #if((line.count("|")!=2) or ("]" not in line) or ("[" not in line)):
        #print "not an event submission"
        #continue
    teststring = submission.title
    testdictionary = {"original":"","game":"","event-title":"","event-desc":"","event-datetime":"","event-host":"","event-url":"","reddit-id":"","discord-id":""}
    
    ##### EATS STRINGS #####
        
    testdictionary["original"]=teststring
    testdictionary["reddit-id"]=submission.shortlink
    testdictionary["discord-id"]="testdiscordid"
    testdictionary["event-host"]=str(submission.author)
    testdictionary["event-url"]=submission.url
        
    # Identifies game string & enters it
    game = teststring.split("]")[:1]
    game = (str(game)[4:(len(str(game))-2)])
    testdictionary["game"] = game
        
    # Identifies and isolates metadata strings
        
    digester = teststring.split("|")
    blanklist = []
        
    stripvalue = len(game)+3
    digester[0] = digester[0][stripvalue:]
    for unit in digester:
        unit = unit.strip()
        blanklist.append(unit)
    
    testdictionary["event-title"]=blanklist[0]
    testdictionary["event-desc"]=blanklist[1]
    
    # Parsing the date into something useful
    print blanklist[2]
    blanklist[2] = blanklist[2].replace(" UTC","")
    print blanklist[2]
    for unit in testdictionary:
        print (unit + " " + testdictionary[str(unit)])
    blanklist[2] = datetime.strptime(blanklist[2],'%a %b%d %H%M')
    # Apply correct year if someone schedules an event early in the next year
    blanklist[2] = blanklist[2].replace(year = datetime.now().year)
    if(blanklist[2].month < datetime.today().month):
        blanklist[2] = blanklist[2].replace(year = (datetime.now().year+1))
        
    testdictionary["event-datetime"]=str(blanklist[2])
        
    for unit in testdictionary:
        print (unit + " " + testdictionary[str(unit)])

    if testdictionary not in jsondictionary:
        jsondictionary.append(testdictionary)
    break

with open('redditevents.json', 'w') as outfile:  
    json.dump(jsondictionary, outfile,indent=4)
                    

