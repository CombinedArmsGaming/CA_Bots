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
DEV_COMMAND = "discordpost"
THANKS_COMMAND = "thanks"

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
	msg = command.replace("discordpost", " ", 1)
        post_discord(str(msg))
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
