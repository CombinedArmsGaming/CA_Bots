import socket
import json
import subprocess
import pickle
import time

HOST = '10.0.0.231'  # Standard loopback interface address (localhost)
PORT = 13131        # Port to listen on (non-privileged ports are > 1023)

def servicetester():
    time.sleep(1)
    call = 'TASKLIST', '/FI', 'imagename eq %s' % 'arma3server.exe'
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith('arma3server.exe'.lower())

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(16384)
                if not data:
                    break
                netcmdraw = json.loads(data)
                netcmdprint = json.dumps(json.loads(data), indent = 2)
                netcmd = eval(netcmdraw)
                
                print(netcmdprint)
                print(netcmd["command"])

                successbool = True

                try:

                    if netcmd["command"] == "radiocheck":
                        #echoes back status as a comms test
                        cmdresponse = {"command":"radiocheck","success":successbool}
                    
                    elif netcmd["command"] == "run":
                        try:
                            #task kills anything called arma3server.exe
                            subprocess.call(["taskkill", "/f", "/im", "arma3server.exe"])
                        except:
                            time.sleep(0.1)

                        try:
                            #starter.bat takes the repo name as an argument then starts the correct HC startup script three times before closing itself.
                            subprocess.call(['C:/Users/CombinedArms/Desktop/STARTER.BAT',str(netcmd["repo"]).upper()])
                        except:
                            successbool = False
                        # check if it fucking did it and reply
                        if ((successbool == True) and (servicetester() == True)):
                            successbool = True
                        else:
                            successbool = False
                        #brag about it
                        cmdresponse = {"command":"run","repo":netcmd["repo"],"success":successbool}

                    elif netcmd["command"] == "kill":
                        # fucking kill it
                        try:
                            #task kills anything called arma3server.exe
                            subprocess.call(["taskkill", "/f", "/im", "arma3server.exe"])
                        except:
                            successbool = False
                        # check if it fucking killed it and reply
                        if ((successbool == True) and (servicetester() == False)):
                            successbool = True
                        else:
                            successbool = False
                        #brag about it
                        cmdresponse = {"command":"kill","success":successbool}
                        

                    elif netcmd["command"] == "query":
                        #echoes back the test result for arma3server.exe instances as a test
                        cmdresponse = {"command":"query","success":servicetester()}

                    elif netcmd["command"] == "update":
                        #splits the payload into a list of mods
                        modlist = netcmd["payload"].split(";")
                        #strips out blank & whitespaced entries
                        modlist[:] = [x for x in modlist if x.strip()]
                        #construct string of correctly formatted filepath combinations for the modline file
                        modstring = ""
                        for x in modlist:
                            modstring = modstring+'S:\\Swifty\\CA\\'+str(x)+";"
                        #save modstring to right file for that repo
                        try:
                            article = open((str(netcmd["repo"]).lower()+"txt.txt"), "w")
                            article.write(modstring)
                            article.close()
                        except:
                            successbool = False
                        #brag about it
                        cmdresponse = {"command":"update","success":successbool,"return":modstring}

                    else:
                        cmdresponse = {"command":netcmd["command"],"success":False,"return":"Error, not recognised"}

                except:
                    cmdresponse = {"command":netcmd["command"],"success":False, "return":"An Error Occurred"}
                    
                returndata = [data,cmdresponse]
                conn.sendall(pickle.dumps(returndata))
