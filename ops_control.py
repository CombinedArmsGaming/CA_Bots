import os
import time
from slackclient import SlackClient
import subprocess

# starterbot's ID as an environment variable
BOT_ID = "U4U1U7M43"

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
TEST_COMMAND = "come in"
HELP_COMMAND = "help"
WEBON_COMMAND = "open repo"
WEBOFF_COMMAND = "close repo"
BUILD_COMMAND = "build repo"
UPDATE_COMMAND = "update repo"

# instantiate Slack & Twilio clients
slack_client = SlackClient('xoxb-164062259139-TDzX0d7XwI9ln8wdxHBBSMB8')


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
    if command.startswith(HELP_COMMAND):
        response = "This is Eagle-Six. My job is to manage the repository automation service. Type open repo or close repo if you need to open/close public access to the repository, or type build repo or update repo if you need to trigger repository construction. I respond to come in as well so you can check if I'm on station"
    if command.startswith(WEBON_COMMAND):
        response = "This is Eagle-Six. Repositories coming live, out."
	subprocess.call("service apache2 start", shell=True)
    if command.startswith(WEBOFF_COMMAND):
        response = "This is Eagle-Six. Repositories going dark, out."
	subprocess.call("service apache2 stop", shell=True)
    if command.startswith(BUILD_COMMAND):
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
    if command.startswith(UPDATE_COMMAND):
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
