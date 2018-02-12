######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VERSION 1.9.4   13/11/2017     ######

"""
    QUICK GLOSSARY
    This updater uses a couple of terms that might not be obvious to the untrained user.
    modfile / modline = list of mods that a client would use to launch Arma 3 in their parameter line
    invfile / invline = "INVerse modLINE" - list of mods in the generation folder that swifty must ignore
                        such that the generated repo contains all the mods in the modline
"""

#############################################
#### IMPORT STATEMENTS                   ####
#############################################

import os
import time
from slackclient import SlackClient
import subprocess
import requests
import json
import re
import sys
import praw
import logging
from datetime import datetime

#############################################
#### LOAD JSON CONFIG DICTIONARIES       ####
#############################################

# Loads JSON data into dictionaries from bot configuration files
with open(os.getcwd()+'/config/botconfig.json') as data_file:    
    botparams = json.load(data_file)[0]
with open(os.getcwd()+'/config/repoconfig.json') as data_file:    
    repoparams = json.load(data_file)
with open(os.getcwd()+'/config/helpfile.json') as data_file:    
    helpfile = json.load(data_file)[0]
with open(os.getcwd()+'/config/discordconfig.json') as data_file:
    discordchannels = json.load(data_file)[0]
with open(os.getcwd()+'/config/redditevents.json') as json_file:  
    redditevents = json.load(json_file)
with open(os.getcwd()+'/config/redditposts.json') as json_file:  
    redditposts = json.load(json_file)


#############################################
#### INSTANTIATE SLACKBOT                ####
#############################################

BOT_ID = botparams["slack-botid"]
slack_client = SlackClient(botparams["slack-token"])

#############################################
#### REDDIT API PARAMETERS               ####
#############################################

reddit = praw.Reddit(client_id=botparams["reddit-client-id"],
                     client_secret=botparams["reddit-client-secret"],
                     password=botparams["reddit-password"],
                     user_agent=botparams["reddit-agent"],
                     username=botparams["reddit-username"])
subreddit = reddit.subreddit('combinedarms')

#############################################
#### DISCORD API HEADERS INIT            ####
#############################################

headers = { "Authorization":botparams["discord-token"],
            "User-Agent":"myBotThing (http://some.url, v0.1)",
            "Content-Type":"application/json", }

#############################################
#### LOGGING CONFIGURATION               ####
#############################################

logging.basicConfig( filename=os.getcwd()+"/bot.log",
                     filemode='w',
                     level=logging.INFO,
                     format= '%(asctime)s - %(levelname)s - %(message)s')

#############################################
#### GLOBAL VARIABLE PRE-SANITISATION    ####
#############################################

AT_BOT = "<@" + BOT_ID + ">"
response = ""
modline = []
invline = []
inputline = []
restarted = False # Used to make sure the bot only ever reinstantiates itself once before killing itself.

#############################################
#### COMMAND PREFIXES                    ####
#############################################

# Commands relating to testing/presence
TEST_COMMAND = "come in"
HELP_COMMAND = "help"
THANKS_COMMAND = "thanks"
DISCORD_COMMAND = "discordpost"
# Commands relating to repository generation
WEBON_COMMAND = "open repo"
WEBOFF_COMMAND = "close repo"
BUILD_COMMAND = "build repo"
UPDATE_COMMAND = "update repo"
SBUILD_COMMAND = "stealth build"
SUPDATE_COMMAND = "stealth update"
# Commands relating to modline generation
MODLINE_COMMAND = "modline"
CHECK_COMMAND = "show"
# Development Command
DEV_COMMAND = "dev" 

#############################################
#############################################
#############################################
####                                     ####
####          COMMAND HANDLER            ####
####                                     ####
#############################################
#############################################
#############################################


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if command.startswith(TEST_COMMAND):
        slackreply("This is Eagle-Six. What do you need?")
    elif command.startswith(DEV_COMMAND):
        slackreply("This is Eagle-Six. Developer command received.")
        msg = command.replace("dev", "", 1)
        gencmd = msg.split(" ")
        subprocess.call("repogen.sh "+gencmd[1]+" "+gencmd[2], shell=True)
        action = str(gencmd[2])
    elif command.startswith(DISCORD_COMMAND):
        msg = command.replace("discordpost", " ", 1)
        msgsplit = msg.split(" ")
        msgsplit[:] = [item for item in msgsplit if item]
        msg = msg.replace(str(msgsplit[0]), "", 1)
        post_discord(str(msgsplit[0]),msg)
    elif command.startswith(MODLINE_COMMAND):
        msg = command.replace("modline", "", 1)
        modcmd = msg.split(" ")
        modlinemanage(str(modcmd[1]),str(modcmd[2]),str(modcmd[3]))
    elif command.startswith(CHECK_COMMAND):
        msg = command.replace("show", "", 1)
        showcmd = msg.split(" ")
        showmanage(str(showcmd[1]))
    elif command.startswith(HELP_COMMAND):
        helpmsg = command[5:]
        helpcommand(helpmsg)
    elif command.startswith(WEBON_COMMAND):
        slackreply("This is Eagle-Six. Repositories coming live, out.")
        subprocess.call("service apache2 start", shell=True)
        post_discord("announcements","@everyone repositories are back up.")
    elif command.startswith(THANKS_COMMAND):
        slackreply("This is Eagle-Six. Anything for Bae, over.")
        subprocess.call("service apache2 start", shell=True)
    elif command.startswith(WEBOFF_COMMAND):
        slackreply("This is Eagle-Six. Repositories going dark, out.")
        subprocess.call("service apache2 stop", shell=True)
        post_discord("announcements","@everyone repositories have been taken down for update.")
    elif command.startswith(BUILD_COMMAND):
        post_discord("announcements","Repositories have been taken down for update.")
        repobuilder("create")
        post_discord("announcements","@everyone repositories have been updated.")
    elif command.startswith(UPDATE_COMMAND):
        post_discord("announcements","Repositories have been taken down for update.")
        repobuilder("update")
        post_discord("announcements","@everyone repositories have been updated.")
    elif command.startswith(SBUILD_COMMAND):
        repobuilder("create")
    elif command.startswith(SUPDATE_COMMAND):
        repobuilder("update")
    else:
    	slackreply("I need more information to allocate additional fire support Parker, try the help command if you need to call for additional support.")

#############################################
#### EXCEPTION LOGGER - USED IN LOG INIT ####
#############################################

def log_exception(e):
    logging.error(
    "Function raised {exception_class} ({exception_docstring}): {exception_message}".format(
    exception_class = e.__class__,
    exception_docstring = e.__doc__,
    exception_message = e.message))

#############################################s
#### SLACK MESSAGE SENDER                ####
#############################################

def slackreply(response):
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

#############################################
#### FILE WRITER - FOR SAVING CONTENT    ####
#############################################

def filewriter(file,string):
    # Simple filewriter that opens the file provided and overwrites the content with the string provided.
    # Strip all line breaks. Line breaks are not approved for use in this software.
    string = re.sub("\n", "", string)
    # Write string to file.
    f = open(file, 'w')
    f.write(string)
    f.close()

#############################################
#### MODLINECOUNTER FOR CONFIDENCE CHECK ####
#############################################

def modlinecount(repo):
    repofile=repochecker(repo)[0]
    with open(repofile, 'r') as f:
        modstring = f.readline()
    modline = modstring.split(";")
    modline[:] = [item for item in modline if item]
    modline = set(modline)
    return (len(modline))    

#############################################
#### DISCORD TEXT OUTPUTTER W CHAN SUPPT ####
#############################################

def post_discord(channel,message):
    # Load message payload
    payload =  json.dumps ( {"content":str(message)} )
    # Make HTTP request using header and payload defined earlier.
    r = requests.post('https://discordapp.com/api/channels/'+discordchannels[str(channel)]+'/messages', headers=headers, data=payload)
    # Prepare error message and overwrite it if the request was successful.
    slackreply(("Returned error code: " + str(r.status_code)))
    if r.status_code == 200:
    	# Tell everyone you've been a good boy
        slackreply("Posted to Discord")


#############################################
#### DISCORD CHANNEL BULK READER         ####
#############################################
    
def get_discord(channel):
    # Make HTTP request using header and payload defined earlier.
    r = requests.get('https://discordapp.com/api/channels/'+discordchannels[str(channel)]+'/messages', headers=headers)
    with open(os.getcwd()+'/config/discordmessages.json', 'w') as outfile:  
        json.dump(r.json(), outfile,indent=4)
    return r.json()

#############################################
#### REDDIT POST MAKER                   ####
#############################################

def post_reddit(post="aar",eventtitle=""):
    global redditposts
    for item in redditposts:
        if((item["postname"] == post) and ((datetime.strptime(item["nextpost"],'%Y-%m-%d %H:%M:%S')) < datetime.now())):
            redditposts.remove(item)

            # MAKE POST ON SUBREDDIT
            subreddit = reddit.subreddit(item["subreddit"])
            subreddit.submit(title=item["posttitle"]+eventtitle, selftext=item["postbody"])
            subreddit = reddit.subreddit('combinedarms')

            # CALCULATE NEXT POST TIME
            calcpost = datetime.strptime(item["nextpost"],'%Y-%m-%d %H:%M:%S')
            if("s" in item["postinterval"]):
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(second = calcpost.second+tempval)
            elif("h" in item["postinterval"]):
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(hour = calcpost.hour+tempval)
            elif("d" in item["postinterval"]):
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(day = calcpost.day+tempval)
            elif("m" in item["postinterval"]):
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(month = calcpost.month+tempval)
            elif("y" in item["postinterval"]):
                tempval = int(re.sub("\D", "", item["postinterval"]))
                item["nextpost"] = calcpost.replace(year = calcpost.year+tempval)
            else:
                item["nextpost"] = calcpost.replace(second = calcpost.second()+1)

            item["nextpost"] = str(item["nextpost"])
            redditposts.append(item)

            # RELOADS POSTS DICTIONARY
            with open(os.getcwd()+'/config/redditposts.json', 'w') as outfile:  
                json.dump(redditposts, outfile,indent=4)
            with open(os.getcwd()+'/config/redditposts.json') as json_file:  
                redditposts = json.load(json_file)

#############################################
#### REPOSITORY CONSTRUCTOR              ####
#############################################

def repobuilder(action):
    # Sanitise action and print beginning message.
    action = str(action)
    slackreply(("This is Eagle-Six to all units. Message received, "+action+" all repositories in succession. Starting Main Repository now, over. (0/3)"))
    # Ensure that all invlines are generated correctly before startup.
    invlinegen("main")
    invlinegen("ww2")
    invlinegen("test")
    # GENERATE MAIN 
    showmanage("main")
    subprocess.call("repogen.sh main "+action, shell=True)
    confirmationmessage("main","ww2","1",action)
    # GENERATE WW2
    showmanage("ww2")
    subprocess.call("repogen.sh ww2 "+action, shell=True)
    confirmationmessage("ww2","test","2",action)
    # GENERATE TEST
    showmanage("test")
    subprocess.call("repogen.sh test "+action, shell=True)
    confirmationmessage("test","fin","3",action)
    # Print confirmation message.
    slackreply(("Eagle-Six to @volc and @klima. Repositories "+action+"d. Eagle-Six out."))

#############################################
#### GENS PROGRESS MESSAGES AS REPO GENS ####
#############################################

def confirmationmessage(repo,nextrepo,count,action):
    # swifty repo.srf is created at the end of a successful repo generation. We can test for it's existence after a generation attempt to check success.
    # Create repo.srf file path identifier
    checkfile = "/var/www/html/"+repo+"/repo.srf"
    # Check for the repo.srf file, and print the right error message.
    if os.path.isfile(checkfile):
        if (nextrepo != "fin"):
            slackreply(("This is Eagle-Six. "+repo+" repository "+action+"d ("+(str(modlinecount(repo)))+" mods). Starting "+nextrepo+" Repository ("+(str(modlinecount(nextrepo)))+" mods), over. ("+str(count)+"/3)"))
            return None
        if (nextrepo == "fin"):
            slackreply(("This is Eagle-Six. "+repo+" repository "+action+"d ("+(str(modlinecount(repo)))+" mods). ("+str(count)+"/3)"))
            return None
    # Print error message if repo.srf doesn't exist.
    slackreply(("There was a problem building "+repo+"repository. @volc should check the console output."))

#############################################
#### CHECKS FOR REPO AND RETNS FILENAMES ####
#############################################

def repochecker(repo):
    if repo == "main":
        repofile = repoparams[0]["repofile"]
        invfile = repoparams[0]["invfile"]
    if repo == "ww2":
        repofile = repoparams[1]["repofile"]
        invfile = repoparams[1]["invfile"]
    if repo == "test":
        repofile = repoparams[2]["repofile"]
        invfile = repoparams[2]["invfile"]
    if (repo != "main") and (repo != "ww2") and (repo != "test"):
        slackreply("Parker, that repository wasn't recognised. Try again, over.")
        return ["",""]
    return [repofile,invfile]

#############################################
#### STRING FORMAT FOR MODLINE CHECKING  ####
#############################################

def showmanage(repo):
    # Check which repo file is to be used and sanity checks it.
    repofile=repochecker(repo)[0]
    invfile=repochecker(repo)[1]
    if (repofile == ""):
        slackreply("Parker, Bannon has made a mistake in the above command. Make sure it gets corrected.")
        return None
    # Open files if they exist and load the contents.
    with open(repofile, 'r') as f:
        modstring = f.readline()
    with open(invfile, 'r') as f:
        invstring = f.readline()
    # Print the contents of the files.
    slackreply(("Parker. The " + repo + "repository contains these "+str(modlinecount(repo))+" mods: " + modstring))
    slackreply(("And Swifty will ignore these mods: " + invstring))

#############################################
#### GENS INVERSE MODLINES FOR STORAGE   ####
#############################################

def invlinegen(repo):
    # Prepares variables for use
    modstring = ""
    invstring = ""
    # Sets variables for chosen repository
    repofile=repochecker(repo)[0]
    invfile=repochecker(repo)[1]
    # Reads in an alphabetical list of all possible mod folders to be used for generation
    inputline = [d for d in os.listdir(botparams["watchfolder"]) if os.path.isdir(os.path.join(botparams["watchfolder"], d))]
    inputline = sorted(inputline)
    # Reads in all the mods in the chosen modline and seperates them into a list 
    with open(repofile, 'r') as f:
        modstring = f.readline()
    modline = modstring.split(";")
    # Generates invline by comparing inputline to modline
    invline = [item for item in inputline if item not in modline]
    # Generates invline string from list
    for mod in invline:
        invstring = (invstring + str(mod)+ ";")
    # Writes invline string to file
    filewriter(invfile,invstring)    

#############################################
#### EXEC EDIT OPERATIONS ON THE MODLINE ####
#############################################

def modlinemanage(operation,mod,repo):
    # Sets variables for chosen repository
    repofile=repochecker(repo)[0]
    invfile=repochecker(repo)[1]

    ### SANITY CHECKS ###
    inputline = [d for d in os.listdir(botparams["watchfolder"]) if os.path.isdir(os.path.join(botparams["watchfolder"], d))]
    inputline = sorted(inputline)
    exist = False
    item = [mod]
    for folder in inputline:
        if (folder == item[0]):
            exist = True

    # Exit if no repo is selected by repochecker, the mod doesn't begin with an @, or the modfolder doesn't exist in the upload folder.
    # As anything can be used for an update command, ignore the tests for folder existing and beginniner with an @ if the command is to do an update.
    if ((repofile == "") or (exist != True) or (item[0][:1] != "@")) and ((operation != "update") or (repofile == "")):
        slackreply("Parker, Bannon has made a mistake in the above command. Make sure it gets corrected. Perhaps the mod folder hasn't been uploaded or the syntax is wrong.")
        return None

    # Reads in all the mods in the chosen modline and seperates them into a list 
    with open(repofile, 'r') as f:
        modstring = f.readline()
    modline = modstring.split(";")

    # IF tree for operation determination
    if operation == "add":
        # Appends mod to active list, removes blank entries, checks for duplicates and then sorts alphabetically.
        modline.append(mod)
        modline[:] = [item for item in modline if item]
        modline = set(modline)
        modline = sorted(modline)
        # Prepares modstring for use, and generates modstring from list.
        modstring = ""
        for mods in modline:
            modstring = (modstring + str(mods)+ ";")
        # Writes modstring to file.
        filewriter(repofile,modstring)
        # Generates invline file from newly updated modline.
        invlinegen(str(repo))
        # ...and tells you what it's done.
        slackreply(("Added " + mod + " to " + repo + " modline, over. (now "+(str(modlinecount(repo)))+" mods)"))
    if operation == "remove":
        # Generates new modline by regenerating modline and omitting mods that match the one being removed.
        gen = [mod]
        modline = [item for item in modline if item not in gen]
        # Removes duplicate mods and sorts alphabetically.
        modline[:] = [item for item in modline if item]
        modline = sorted(modline)
        # Prepares modstring for use, and generates new modfile string. 
        modstring = ""
        for mods in modline:
            modstring = (modstring + str(mods)+ ";")
        # Writes modline string to file.
        filewriter(repofile,modstring)
        # Generates invline from newly generated modline.
        invlinegen(str(repo))
        # Then tells everyone it's a clever boy.
        slackreply(("Removed " + mod + " from " + repo + " modline, over. (now "+(str(modlinecount(repo)))+" mods)"))
    if operation == "update":
        # Doesn't give a damn, just generates an invline.
        invlinegen(str(repo))
        # Tells you it's done it.
        slackreply(("Updated " + repo + " modline, over."))
    if (operation != "add") and (operation != "remove") and (operation != "update"):
        # Chastises you for being silly
        slackreply("Parker, I need to know what to do to the modline. Try telling me to add remove or update the modline.")
        return None

#############################################
#### MANAGES THE HELP FUNCTION           ####
#############################################

def helpcommand(command):
    # Checks if string entered was just the word "help" and then santises it for the JSON lookup.
    if (str(command) == ""):
        command = "help"
    # tries/catches to check the helpfile for a key entry that matches the user request
    try:
        slackreply((str(helpfile[command]["helptext"])))
    # handles moron users
    except KeyError:
        slackreply("I didn't understand that help request Parker. Try typing Help List for a list of possible commands.")

#############################################
#### PROCESSES REDDIT EVENT POSTS        ####
#############################################

def eventposthandle(submission):
    eventstring = submission.title
    if((eventstring.count("|")!=2) or ("]" not in eventstring) or ("[" not in eventstring)):
        return
    postdictionary = {"original":"","game":"","event-title":"","event-desc":"","event-datetime":"","event-host":"","event-url":"","reddit-id":""}
    
    ##### EATS STRINGS #####
        
    postdictionary["original"]=eventstring
    postdictionary["reddit-id"]=submission.shortlink
    postdictionary["event-host"]=str(submission.author)
    postdictionary["event-url"]=submission.url
        
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
    
    postdictionary["event-title"]=blanklist[0]
    postdictionary["event-desc"]=blanklist[1]
    
    # Parsing the date into something useful
    blanklist[2] = blanklist[2].replace(" UTC","")
    try:
        blanklist[2] = datetime.strptime(blanklist[2],'%a %b%d %H%M')
        # Apply correct year if someone schedules an event early in the next year
        blanklist[2] = blanklist[2].replace(year = datetime.now().year)
        if(blanklist[2].month < datetime.today().month):
            blanklist[2] = blanklist[2].replace(year = (datetime.now().year+1))    
        postdictionary["event-datetime"]=str(blanklist[2])
    except:
        postdictionary["event-datetime"]="2000-04-01 19:00:00"
    nowdate = datetime.now()
    postdate = datetime.strptime(postdictionary["event-datetime"],'%Y-%m-%d %H:%M:%S')
    postdate = postdate.replace(hour = postdate.hour)
    if (postdictionary not in redditevents) and (postdate > nowdate):
        redditevents.append(postdictionary)
        post_discord("events",postdictionary["event-url"])
    with open(os.getcwd()+'/config/redditevents.json', 'w') as outfile:  
        json.dump(redditevents, outfile,indent=4)

#############################################
#### SLACK CONTENT STRING PROCESSOR      ####
#############################################

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

#############################################
#### MAIN PROCESS THREAD                 ####
#############################################

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Operations Controller connected and running!")
        while True:
            try:
                try:
                    command, channel = parse_slack_output(slack_client.rtm_read())
                except:
                    print "Connection Broken"
                    if not restarted:
                        restarted = True
                        subprocess.call(os.getcwd()+'/cronjob.sh', shell=True)
                        sys.exit()
                if command and channel:
                    handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
                for submission in subreddit.new(limit=1):
                    eventposthandle(submission)
                    break
                eventscontent = get_discord("events")
                for item in eventscontent:
                    for post in redditevents:
                        if str(post["reddit-id"][-6:]) in str(item):
                            postdate = datetime.strptime(post["event-datetime"],'%Y-%m-%d %H:%M:%S')
                            postdate = postdate.replace(hour = postdate.hour)
                            nowdate = datetime.now()
                            if postdate < nowdate:
                                redditevents.remove(post)
                                with open(os.getcwd()+'/config/redditevents.json', 'w') as outfile:  
                                    json.dump(redditevents, outfile,indent=4)
                                r = requests.delete('https://discordapp.com/api/channels/'+discordchannels["events"]+'/messages/'+item["id"], headers=headers)
                                post_reddit(post="aar",eventtitle=post["event-title"])
                                with open(os.getcwd()+'/config/redditevents.json') as json_file:  
                                    redditevents = json.load(json_file)
            except Exception as e:
                log_exception(e)
                
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
