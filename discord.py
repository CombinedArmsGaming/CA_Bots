######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VER INFO IN MAIN.PY 13/2/2018  ######

'''All the functions for Colonel Sawyer relating to the Discord integration'''

import os
import json
import requests
from globalvar import discordchannels, headers, slackreply

#############################################
#### DISCORD TEXT OUTPUTTER W CHAN SUPPT ####
#############################################

def post_discord(channel, message):
    '''Posts text to discord with channel support'''
    # Load message payload
    payload = json.dumps({"content":str(message)})
    # Make HTTP request using header and payload defined earlier.
    url = ('https://discordapp.com/api/channels/'+discordchannels[str(channel)]+'/messages')
    make_req = requests.post(url, headers=headers, data=payload)
    # Prepare error message and overwrite it if the request was successful.
    slackreply(("Returned error code: " + str(make_req.status_code)))
    if make_req.status_code == 200:
    	# Tell everyone you've been a good boy
        slackreply("Posted to Discord")


#############################################
#### DISCORD CHANNEL BULK READER         ####
#############################################

def get_discord(channel):
    '''Draws all posts from a discord channel'''
    # Make HTTP request using header and payload defined earlier.
    url = ('https://discordapp.com/api/channels/'+discordchannels[str(channel)]+'/messages')
    make_req = requests.get(url, headers=headers)
    with open(os.getcwd()+'/config/discordmessages.json', 'w') as outfile:
        json.dump(make_req.json(), outfile, indent=4)
    return make_req.json()
