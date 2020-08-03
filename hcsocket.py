######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VER INFO IN MAIN.PY 02/8/2020  ######

'''All the functions for Colonel Sawyer relating to the HC Socket integration'''

from __future__ import absolute_import
import json
import socket
import pickle
from globalvar import hcdetails

#############################################
#### REDDIT POST MAKER                   ####
#############################################

def sendtohc(command="radiocheck",repo="",payload=""):

    '''This code communicates with the HC server and returns the reponses'''


    HCHOST = hcdetails["hcip"]  # The server's hostname or IP address
    HCPORT = hcdetails["hcport"]        # The port used by the server

    netcmdjson = json.dumps(netcmddict)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HCHOST, HCPORT))
        s.sendall(bytes(netcmdjson,encoding="utf-8"))
        data = s.recv(16384)
        returndata = eval((repr(pickle.loads(data))))
    return(returndata)