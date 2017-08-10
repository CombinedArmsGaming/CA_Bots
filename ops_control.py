import os
import time
from slackclient import SlackClient
import subprocess
import requests
import json

# Instantiate Slackbot
BOT_ID = "XXXXXXXXXXX"
slack_client = SlackClient('XXXXXXXXXXX')

headers = { "Authorization":"Bot XXXXXXXXXXX",
            "User-Agent":"myBotThing (http://some.url, v0.1)",
            "Content-Type":"application/json", }


# constants
AT_BOT = "<@" + BOT_ID + ">"

EXAMPLE_COMMAND = "do"
TEST_COMMAND = "come in"
HELP_COMMAND = "help"
WEBON_COMMAND = "open repo"
WEBOFF_COMMAND = "close repo"
BUILD_COMMAND = "build repo"
UPDATE_COMMAND = "update repo"
SBUILD_COMMAND = "stealth build"
SUPDATE_COMMAND = "stealth update"
DISCORD_COMMAND = "discordpost"
THANKS_COMMAND = "thanks"
DEV_COMMAND = "dev"
MODLINE_COMMAND = "modline"
response = ""

modline = []
invline = []
inputline = []

def post_discord(message):
    payload =  json.dumps ( {"content":str(message)} )
    r = requests.post('https://discordapp.com/api/channels/XXXXXXXXXXX/messages', headers=headers, data=payload)
    response = ("Returned error code: " + str(r.status_code))
    if r.status_code == 200:
        response = "Posted to Discord"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)



def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I need more information to allocate additional fire support Parker, try the help command if you need to call for additional support."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Eagle Six to Bannon; Give me a SITREP."
    if command.startswith(TEST_COMMAND):
        response = "This is Eagle-Six. What do you need?"
    if command.startswith(DEV_COMMAND):
        response = "This is Eagle-Six. Developer command received."
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        invlinegen("main")
    if command.startswith(DISCORD_COMMAND):
        msg = command.replace("discordpost", " ", 1)
        post_discord(str(msg))
        response = ""
    if command.startswith(MODLINE_COMMAND):
        msg = command.replace("modline", "", 1)
        modcmd = msg.split(" ")
        modlinemanage(str(modcmd[1]),str(modcmd[2]),str(modcmd[3]))
        response = ""
    if command.startswith(HELP_COMMAND):
        response = "This is Eagle-Six. My job is to manage the repository automation service. Using discordpost <message> will post a short message to Discord. Type open repo or close repo if you need to open/close public access to the repository, or type build repo or update repo if you need to trigger repository construction. I respond to come in as well so you can check if I'm on station"
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
        response = "This is Eagle-Six to all units. Building all repositories in succession. Starting Main Repository now, over."
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        print("Building all repositories.")
        subprocess.call("maingen.sh", shell=True)
        response = "This is Eagle-Six. Main Repository Built. Starting WW2 Repository, over. (1/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("ww2gen.sh", shell=True)
        response = "This is Eagle-Six. WW2 Repository Built. Starting Test Repository, over. (2/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("testgen.sh", shell=True)
        response = "This is Eagle-Six. Test Repository Built, over. (3/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = "Eagle-Six to @volc and @klima. Repositories built. Eagle-Six out."
        post_discord("@everyone repositories have been updated.")
    if command.startswith(UPDATE_COMMAND):
        post_discord("Repositories have been taken down for update.")
        response = "This is Eagle-Six to all units. Updating all repositories in succession. Starting Main Repository now, over. (0/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        print("Updating all repositories.")
        subprocess.call("mainupd.sh", shell=True)
        response = "This is Eagle-Six. Main Repository Updated. Starting WW2 Repository, over. (1/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("ww2upd.sh", shell=True)
        response = "This is Eagle-Six. WW2 Repository Updated. Starting Test Repository, over. (2/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("testupd.sh", shell=True)
        response = "This is Eagle-Six. Test Repository Updated, over. (3/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = "Eagle-Six to @volc and @klima. Repositories updated. Eagle-Six out."
        post_discord("@everyone repositories have been updated.")
    if command.startswith(SBUILD_COMMAND):
        response = "This is Eagle-Six to all units. Silently building all repositories in succession. Starting Main Repository now, over."
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        print("Building all repositories.")
        subprocess.call("maingen.sh", shell=True)
        response = "This is Eagle-Six. Main Repository Built. Starting WW2 Repository, over. (1/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("ww2gen.sh", shell=True)
        response = "This is Eagle-Six. WW2 Repository Built. Starting Test Repository, over. (2/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("testgen.sh", shell=True)
        response = "This is Eagle-Six. Test Repository Built, over. (3/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = "Eagle-Six to @volc and @klima. Repositories silently built. Eagle-Six out."
    if command.startswith(SUPDATE_COMMAND):
        response = "This is Eagle-Six to all units. Silently updating all repositories in succession. Starting Main Repository now, over. (0/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        print("Updating all repositories.")
        subprocess.call("mainupd.sh", shell=True)
        response = "This is Eagle-Six. Main Repository Updated. Starting WW2 Repository, over. (1/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("ww2upd.sh", shell=True)
        response = "This is Eagle-Six. WW2 Repository Updated. Starting Test Repository, over. (2/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        subprocess.call("testupd.sh", shell=True)
        response = "This is Eagle-Six. Test Repository Updated, over. (3/3)"
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        response = "Eagle-Six to @volc and @klima. Repositories silently updated. Eagle-Six out."
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def invlinegen(repo):
    modstring = ""
    invstring = ""
    # Sets variables for chosen repository
    if repo == "main":
    	repofile = "/repository/storage/mainmodline"
    	invfile = "/repository/storage/mainignore"
    if repo == "ww2":
    	repofile = "/repository/storage/ww2modline"
    	invfile = "/repository/storage/ww2ignore"
    if repo == "test":
    	repofile = "/repository/storage/testmodline"
    	invfile = "/repository/storage/testignore"
    if (repo != "main") and (repo != "ww2") and (repo != "test"):
    	print "this repository was not recognised"
    	return None
    # Reads in an alphabetical list of all possible mod folders to be used for generation
    inputline = [d for d in os.listdir("/repository/input") if os.path.isdir(os.path.join("/repository/input", d))]
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
    f = open(invfile, 'w')
    f.write(invstring)
    f.close()    

def modlinemanage(operation,mod,repo):
    if str(repo) == "main":
    	repofile = "/repository/storage/mainmodline"
    	invfile = "/repository/storage/mainignore"
    if str(repo) == "ww2":
    	repofile = "/repository/storage/ww2modline"
    	invfile = "/repository/storage/ww2ignore"
    if str(repo) == "test":
    	repofile = "/repository/storage/testmodline"
    	invfile = "/repository/storage/testignore"
    if (str(repo) != "main") and (str(repo) != "ww2") and (str(repo) != "test"):
        print "this repo was not recognised"
        return None

    # Reads in all the mods in the chosen modline and seperates them into a list 
    with open(repofile, 'r') as f:
        modstring = f.readline()
    modline = modstring.split(";")
    # IF tree for operation determination
    if operation == "add":
        modline.append(mod)
        modline[:] = [item for item in modline if item]
        modline = sorted(modline)
        modstring = ""
        for mods in modline:
    	    modstring = (modstring + str(mods)+ ";")
        f = open(repofile, 'w')
        f.write(modstring)
        f.close()
        invlinegen(str(repo))
        response = ("Added " + mod + " to " + repo + " modline, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    if operation == "remove":
    	gen = [mod]
        modline = [item for item in modline if item not in gen]
        modline[:] = [item for item in modline if item]
        modline = sorted(modline)
        modstring = ""
        for mods in modline:
    	    modstring = (modstring + str(mods)+ ";")
    	f = open(repofile, 'w')
        f.write(modstring)
        f.close()
        invlinegen(str(repo))
        response = ("Removed " + mod + " from " + repo + " modline, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    if operation == "update":
        invlinegen(str(repo))
        response = ("Updating " + repo + " modline, over.")
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    if (operation != "add") and (operation != "remove") and (operation != "update"):
        print "this operation was not recognised"
        return None

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
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")