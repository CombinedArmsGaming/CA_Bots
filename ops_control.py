######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VERSION 1.7     3/10/2017      ######

"""
    QUICK GLOSSARY
    This updater uses a couple of terms that might not be obvious to the untrained user.
    modfile / modline = list of mods that a client would use to launch Arma 3 in their parameter line
    invfile / invline = "INVerse modLINE" - list of mods in the generation folder that swifty must ignore
                        such that the generated repo contains all the mods in the modline
"""

import os
import time
from slackclient import SlackClient
import subprocess
import requests
import json
import re
import sys

# Loads JSON data into dictionaries from bot configuration files
with open('/python/slackbot/botconfig.json') as data_file:    
    botparams = json.load(data_file)[0]
with open('/python/slackbot/repoconfig.json') as data_file:    
    repoparams = json.load(data_file)

# Instantiate Slackbot
BOT_ID = botparams["slack-botid"]
slack_client = SlackClient(botparams["slack-token"])
# Discord HTTP header initialisation
headers = { "Authorization":botparams["discord-token"],
            "User-Agent":"myBotThing (http://some.url, v0.1)",
            "Content-Type":"application/json", }

# Global Variable Pre-Sanitisation
AT_BOT = "<@" + BOT_ID + ">"
response = ""
modline = []
invline = []
inputline = []
restarted = False # Used to make sure the bot only ever reinstantiates itself once before killing itself.

###### COMMAND PREFIXES ######

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

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I need more information to allocate additional fire support Parker, try the help command if you need to call for additional support."
    if command.startswith(TEST_COMMAND):
        response = "This is Eagle-Six. What do you need?"
    if command.startswith(DEV_COMMAND):
        response = "This is Eagle-Six. Developer command received."
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        msg = command.replace("dev", "", 1)
        gencmd = msg.split(" ")
        subprocess.call("repogen.sh "+gencmd[1]+" "+gencmd[2], shell=True)
        response = ""
        action = str(gencmd[2])
    if command.startswith(DISCORD_COMMAND):
        msg = command.replace("discordpost", " ", 1)
        post_discord(str(msg))
        response = ""
    if command.startswith(MODLINE_COMMAND):
        msg = command.replace("modline", "", 1)
        modcmd = msg.split(" ")
        modlinemanage(str(modcmd[1]),str(modcmd[2]),str(modcmd[3]))
        response = ""
    if command.startswith(CHECK_COMMAND):
        msg = command.replace("show", "", 1)
        showcmd = msg.split(" ")
        showmanage(str(showcmd[1]))
        response = ""
    if command.startswith(HELP_COMMAND):
	helpmsg = command[5:]
	helpcommand(helpmsg)
	response = ""
    if command.startswith(WEBON_COMMAND):
        response = "This is Eagle-Six. Repositories coming live, out."
        subprocess.call("service apache2 start", shell=True)
        post_discord("@everyone repositories are back up.")
    if command.startswith(THANKS_COMMAND):
        response = "This is Eagle-Six. Anything for Bae, over."
        subprocess.call("service apache2 start", shell=True)
    if command.startswith(WEBOFF_COMMAND):
        response = "This is Eagle-Six. Repositories going dark, out."
        subprocess.call("service apache2 stop", shell=True)
        post_discord("@everyone repositories have been taken down for update.")
    if command.startswith(BUILD_COMMAND):
        post_discord("Repositories have been taken down for update.")
        repobuilder("create")
        post_discord("@everyone repositories have been updated.")
        response = ""
    if command.startswith(UPDATE_COMMAND):
        post_discord("Repositories have been taken down for update.")
        repobuilder("update")
        post_discord("@everyone repositories have been updated.")
        response = ""
    if command.startswith(SBUILD_COMMAND):
        repobuilder("create")
        response = ""
    if command.startswith(SUPDATE_COMMAND):
        repobuilder("update")
        response = ""
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def post_discord(message):
	# Load message payload
    payload =  json.dumps ( {"content":str(message)} )
    # Make HTTP request using header and payload defined earlier.
    r = requests.post('https://discordapp.com/api/channels/'+botparams["discord-channel"]+'/messages', headers=headers, data=payload)
    # Prepare error message and overwrite it if the request was successful.
    response = ("Returned error code: " + str(r.status_code))
    if r.status_code == 200:
        response = "Posted to Discord"
    # Tell everyone you've been a good boy
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def repobuilder(action):
	# Sanitise action and print beginning message.
    action = str(action)
    print(action+" - all repositories.")
    response = "This is Eagle-Six to all units. Message received, silently "+action+" all repositories in succession. Starting Main Repository now, over. (0/3)"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
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
    response = "Eagle-Six to @volc and @klima. Repositories "+action+"d. Eagle-Six out."
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def confirmationmessage(repo,nextrepo,count,action):
	# swifty repo.srf is created at the end of a successful repo generation. We can test for it's existence after a generation attempt to check success.
    # Create repo.srf file path identifier
    checkfile = "/var/www/html/"+repo+"/repo.srf"
    # Check for the repo.srf file, and print the right error message.
    if os.path.isfile(checkfile):
        if (nextrepo != "fin"):
            response = "This is Eagle-Six. "+repo+" repository "+action+"d. Starting "+nextrepo+" Repository, over. ("+str(count)+"/3)"
            slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            return None
        if (nextrepo == "fin"):
            response = "This is Eagle-Six. "+repo+" repository "+action+"d. ("+str(count)+"/3)"
            slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            return None
    # Print error message if repo.srf doesn't exist.
    response = "There was a problem building "+repo+"repository. @volc should check the console output."
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

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
        print "this repository was not recognised"
        response = ("Parker, that repository wasn't recognised. Try again, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return ["",""]
    return [repofile,invfile]

def filewriter(file,string):
    # Simple filewriter that opens the file provided and overwrites the content with the string provided.
    # Strip all line breaks. Line breaks are not approved for use in this software.
    string = re.sub("\n", "", string)
    # Write string to file.
    f = open(file, 'w')
    f.write(string)
    f.close()

def showmanage(repo):
	# Check which repo file is to be used and sanity checks it.
    repofile=repochecker(repo)[0]
    invfile=repochecker(repo)[1]
    if (repofile == ""):
        response = ("Parker, Bannon has made a mistake in the above command. Make sure it gets corrected.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return None
    # Open files if they exist and load the contents.
    with open(repofile, 'r') as f:
        modstring = f.readline()
    with open(invfile, 'r') as f:
        invstring = f.readline()
    # Print the contents of the files.
    response = ("Parker. The " + repo + "repository contains these mods: " + modstring)
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    response = ("And Swifty will ignore these mods: " + invstring)
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

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
        response = ("Parker, Bannon has made a mistake in the above command. Make sure it gets corrected. Perhaps the mod folder hasn't been uploaded or the syntax is wrong.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
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
        response = ("Added " + mod + " to " + repo + " modline, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
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
        response = ("Removed " + mod + " from " + repo + " modline, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    if operation == "update":
        # Doesn't give a damn, just generates an invline.
        invlinegen(str(repo))
        # Tells you it's done it.
        response = ("Updated " + repo + " modline, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    if (operation != "add") and (operation != "remove") and (operation != "update"):
        # Chastises you for being silly
        print "this operation was not recognised"
        response = ("Parker, I need to know what to do to the modline. Try telling me to add remove or update the modline.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return None

def helpcommand(command):
    try:
        print(data[command]["helptext"])
    except KeyError:
        print("ID doesn't exist")

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

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Operations Controller connected and running!")
        while True:
            try:
                command, channel = parse_slack_output(slack_client.rtm_read())
            except:
                print "Connection Broken"
                if not restarted:
                    restarted = True
                    subprocess.call("/python/slackbot/cronjob.sh", shell=True)
                    sys.exit()
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
