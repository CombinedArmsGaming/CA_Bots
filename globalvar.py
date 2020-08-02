######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VER INFO IN MAIN.PY 25/2/2018  ######

from __future__ import absolute_import
import json
import os
import re
import praw
from slackclient import SlackClient

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
#### GLOBAL VARIABLE PRE-SANITISATION    ####
#############################################

AT_BOT = "<@" + BOT_ID + ">"
response = ""
modline = []
invline = []
inputline = []
# Used to make sure the bot only ever reinstantiates itself once before killing itself.
restarted = False

#############################################
#### COMMAND PREFIXES                    ####
#############################################

prefixes = {# Commands relating to testing/presence
    "TEST_COMMAND":"come in",
    "HELP_COMMAND":"help",
    "THANKS_COMMAND":"thanks",
    "DISCORD_COMMAND":"discordpost",
    # Commands relating to repository management
    "WEBON_COMMAND":"open repo",
    "WEBOFF_COMMAND":"close repo",
    "BUILD_COMMAND":"build repo",
    "SBUILD_COMMAND":"stealth build",
    "MODLINE_COMMAND":"modline",
    "CHECK_COMMAND":"show",
    "SINGLEBUILD_COMMAND":"single",
    # Development Command
    "DEV_COMMAND":"dev"}

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

headers = {"Authorization":botparams["discord-token"],
           "User-Agent":"myBotThing (http://some.url, v0.1)",
           "Content-Type":"application/json"}

#############################################
#### HC IP CONFIG DETAILS                ####
#############################################

hcdetails = {"hcip":botparams["hcip"],"hcport":botparams[hcport]}

#############################################
#### SLACK MESSAGE SENDER                ####
#############################################

def slackreply(response):
    slack_client.api_call("chat.postMessage", channel=botparams["slack-channel"], text=response, as_user=True)

#############################################
#### FILE WRITER - FOR SAVING CONTENT    ####
#############################################

def filewriter(filew, string):
    # Simple filewriter that opens the file and overwrites the content with the string provided.
    # Strip all line breaks. Line breaks are not approved for use in this software.
    string = re.sub("\n", "", string)
    # Write string to file.
    openfile = open(filew, 'w')
    openfile.write(string)
    openfile.close()
