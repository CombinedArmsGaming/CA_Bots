######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VERSION 2.1.0   02/08/2020     ######

"""
    QUICK GLOSSARY
    This updater uses a couple of terms that might not be obvious to the untrained user.
    modfile / modline = list of mods that a client would use to launch A3 in their parameter line
    invfile / invline = "INVerse modLINE" - list of mods in the gen folder that swifty must ignore
                        such that the generated repo contains all the mods in the modline
"""

#############################################
#### IMPORT STATEMENTS                   ####
#############################################

from __future__ import absolute_import
import os
import time
import subprocess
import json
import sys
import logging
from datetime import datetime
import requests
from discord import post_discord, get_discord
from reddit import post_reddit, eventposthandle
from repo import repobuilder, modlinemanage, showmods, reposingle, hcupdater
from globalvar import helpfile, discordchannels, redditevents, slack_client, AT_BOT, restarted, prefixes, subreddit, headers, slackreply
from hcsocket import sendtohc

#############################################
#### LOGGING CONFIGURATION               ####
#############################################

logging.basicConfig(filename=os.getcwd()+"/bot.log",
                    filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
    if command.startswith(prefixes["TEST_COMMAND"]):
        slackreply("This is Eagle-Six. What do you need?")
    elif command.startswith(prefixes["DEV_COMMAND"]):
        slackreply("This is Eagle-Six. Developer command received.")
        postdate = datetime.strptime(redditevents[0]["event-datetime"], '%Y-%m-%d %H:%M:%S')
        post_discord("aar",("~~-                                                                   -~~\n**"+redditevents[0]["event-title"].upper()+"**\n**"+str(postdate)+"**\n"+post["event-url"]+"\n~~-                                                                   -~~"))
    elif command.startswith(prefixes["DISCORD_COMMAND"]):
        msg = command.replace("discordpost", " ", 1)
        msgsplit = msg.split(" ")
        msgsplit[:] = [item for item in msgsplit if item]
        msg = msg.replace(str(msgsplit[0]), "", 1)
        post_discord(str(msgsplit[0]), msg)
    elif command.startswith(prefixes["MODLINE_COMMAND"]):
        msg = command.replace("modline", "", 1)
        modcmd = msg.split(" ")
        modlinemanage(str(modcmd[1]), str(modcmd[2]), str(modcmd[3]))
    elif command.startswith(prefixes["CHECK_COMMAND"]):
        msg = command.replace("show", "", 1)
        showcmd = msg.split(" ")
        showmods(showcmd[1])
    elif command.startswith(prefixes["HELP_COMMAND"]):
        helpmsg = command[5:]
        helpcommand(helpmsg)
    elif command.startswith(prefixes["WEBON_COMMAND"]):
        slackreply("This is Eagle-Six. Repositories coming live, out.")
        subprocess.call("service apache2 start", shell=True)
        post_discord("announcements", "@everyone repositories are back up.")
    elif command.startswith(prefixes["WEBOFF_COMMAND"]):
        slackreply("This is Eagle-Six. Repositories going dark, out.")
        subprocess.call("service apache2 stop", shell=True)
    elif command.startswith(prefixes["THANKS_COMMAND"]):
        slackreply("This is Eagle-Six. Anything for Bae, over.")
        subprocess.call("service apache2 start", shell=True)
        post_discord("announcements", "@everyone repositories have been taken down for update.")
    elif command.startswith(prefixes["BUILD_COMMAND"]):
        post_discord("announcements", "Repositories have been taken down for update.")
        repobuilder(True)
    elif command.startswith(prefixes["SBUILD_COMMAND"]):
        repobuilder(False)
    elif command.startswith(prefixes["SINGLEBUILD_COMMAND"]):
        msg = command.replace("single", "", 1)
        showcmd = msg.split(" ")
        reposingle(str(showcmd[1]))
    elif command.startswith(prefixes["HCUPDATE_COMMAND"]):
        msg = command.replace("hcupdate", "", 1)
        hcupdatemsg = msg.split(" ")
        hcresponse = hcupdater(str(hcupdatemsg[1]))
        if ((hcresponse[1]["success"]) and (hcresponse[1]["command"] == "update")):
            slackreply("Headless Client reports repo parameters updated successfully.")
        elif (hcreponse == None):
            slackreply("No response from telemetry unit.")
        else:
            slackreply("Faulty response from telemetry unit.")
    elif command.startswith(prefixes["HCKILL_COMMAND"]):
        hcresponse = sendtohc(command="kill")
        if ((hcresponse[1]["success"]) and (hcresponse[1]["command"] == "kill")):
            slackreply("Headless Clients successfully killed")
        elif (hcreponse == None):
            slackreply ("No response from HC server.")
        else:
            slackreply("Headless Client kill not confirmed. Return from HC server reads: "+str(hcresponse))
    elif command.startswith(prefixes["HCQUERY_COMMAND"]):
        hcresponse = sendtohc(command="query")
        if ((hcresponse[1]["success"]) and (hcresponse[1]["command"] == "query")):
            slackreply("Headless Client processes are operating. This does not guarantee that the processes are running correctly.")
        elif ((not(hcresponse[1]["success"])) and (hcresponse[1]["command"] == "query")):
            slackreply("Headless Client processes are not operating.")
        elif (hcreponse == None):
            slackreply("No response from telemetry unit.")
        else:
            slackreply("Faulty response from telemetry unit.")
    elif command.startswith(prefixes["HCSTART_COMMAND"]):
        msg = command.replace("hcstart", "", 1)
        hcstartcmd = msg.split(" ")
        hcresponse = sendtohc(command="run",repo=str(hcstartcmd[1]))
        if ((hcresponse[1]["success"]) and (hcresponse[1]["command"] == "run")):
            slackreply("Headless Client Server reports the clients have started.")
        elif (hcreponse == None):
            slackreply("No response from telemetry unit.")
        else:
            slackreply("Faulty response from telemetry unit.")
    elif command.startswith(prefixes["HCRADIOCHECK_COMMAND"]):
        hcresponse = sendtohc(command="radiocheck")
        if ((hcresponse[1]["success"]) and (hcresponse[1]["command"] == "radiocheck")):
            slackreply("Headless Client Server is responding to telemetry.")
        elif (hcreponse == None):
            slackreply("No response from telemetry unit.")
        else:
            slackreply("Faulty response from telemetry unit.")
    else:
        slackreply("I need more information to allocate additional fire support Parker, try the help command if you need to call for additional support.")

#############################################
#### EXCEPTION LOGGER - USED IN LOG INIT ####
#############################################

def log_exception(e):
    logging.error(
        "Function raised {exception_class} ({exception_docstring}): {exception_message}".format(
            exception_class=e.__class__,
            exception_docstring=e.__doc__,
            exception_message=str(e)))

#############################################
#### MANAGES THE HELP FUNCTION           ####
#############################################

def helpcommand(command):
    # Checks if string entered was just the word "help" and then santises it for the JSON lookup.
    if str(command) == "":
        command = "help"
    # tries/catches to check the helpfile for a key entry that matches the user request
    try:
        slackreply((str(helpfile[command]["helptext"])))
    # handles moron users
    except KeyError:
        slackreply("I didn't understand that help request Parker. Try typing Help List for a list of possible commands.")

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
                    print("Connection Broken")
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
                            postdate = datetime.strptime(post["event-datetime"], '%Y-%m-%d %H:%M:%S')
                            postdate = postdate.replace(hour=postdate.hour)
                            nowdate = datetime.now()
                            if postdate < nowdate:
                                redditevents.remove(post)
                                with open(os.getcwd()+'/config/redditevents.json', 'w') as outfile:
                                    json.dump(redditevents, outfile, indent=4)
                                r = requests.delete('https://discordapp.com/api/channels/'+discordchannels["events"]+'/messages/'+item["id"], headers=headers)
                                #post_reddit(post="aar", eventtitle=post["event-title"])
                                post_discord("aar",("~~-                                                                   -~~\n**"+post["event-title"].upper()+"**\n**"+str(postdate)+"**\n"+post["event-url"]+"\n~~-                                                                   -~~"))
                                with open(os.getcwd()+'/config/redditevents.json') as json_file:
                                    redditevents = json.load(json_file)
            except Exception as e:
                log_exception(e)

    else:
        print("Connection failed. Invalid Slack token or bot ID?")
