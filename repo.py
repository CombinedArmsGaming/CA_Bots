######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VER INFO IN MAIN.PY 25/2/2018  ######

'''This module contains all the repository management functions'''

from __future__ import absolute_import
import os
import subprocess
from globalvar import filewriter, slackreply, botparams, repoparams

#############################################
#### REPOSITORY CONSTRUCTOR              ####
#############################################

def repobuilder():
    '''This function handles the repository construction'''
    # Sanitise action and print beginning message.
    slackreply(("This is Eagle-Six to all units. Message received, build all repositories in succession, over."))
    for r in repoparams:
        subprocess.call("r3pogen.sh "+str(r["name"]), shell=True)
        confirmationmessage(str(r["name"]))
    # Print confirmation message.
    slackreply(("Eagle-Six to @volc and @klima. Repositories built. Eagle-Six out."))

#############################################
####  GENS ERROR MESSAGES AS REPO GENS   ####
#############################################

def confirmationmessage(repo):
    '''Formats and prints mid-repository construction updates to Slack.'''
    # swifty repo.srf is created at the end of a successful repo generation.
    # We can test for it's existence after a generation attempt to check success.
    # Create repo.json file path identifier
    checkfile = "/var/www/html/"+repo+"/repo.json"
    # Check for the repo.srf file, and print the right error message.
    if !(os.path.isfile(checkfile)):
        # Print error message if repo.json doesn't exist.
        slackreply(("There was a problem building "+repo+"repository. @volc should check the console output."))
    return None

#############################################
#### CHECKS FOR REPO AND RETURNS BOOLEAN ####
#############################################

def repochecker(repo):
    '''Checks if a repository exists and returns the locations of the relevant config files'''
    for r in repoparams:
        if r["name"]==repo:
            return True
    print("Parker, that repository wasn't recognised. Try again, over.")
    return False

#############################################
#### EXEC EDIT OPERATIONS ON THE MODLINE ####
#############################################

def modlinemanage(operation, mod, repo):
    '''Manages the modline addtion/removal operations'''

    repojson=True
    repomods=[]

    for r in repoparams:
        if r["name"]==repo:
            with open('/repository/storage/'+str(repo)+'repo.json') as data_file:
            repojson = json.load(data_file)

    for x in repojson["requiredMods"]:
        repomods.append(x["modName"])

    #############################################
    ####   VALIDATION OF COMMAND FROM USER   ####
    #############################################

    # Operation Validation
    if (operation!="add") and (operation!="remove"):
        # Chastises you for being silly
        slackreply("Parker, I need to know what to do to the modline. Try telling me to add or remove from the modline.")
        return None

    # Repository Validation
    if repochecker(repo)==False:
        slackreply("Parker, this repository doesn't exist. Re-check your information and try again.")
        return None

    # Mod Validation
    if mod[:1]!="@":
        slackreply("Parker, that mod doesn't begin with an @. Try again.")
        return None
    if operation=="remove":
        if mod not in repomods:
            slackreply("Parker, you can't remove a mod that isn't in the repository")
    if operation=="add":
        inputline = [d for d in os.listdir(botparams["watchfolder"]) if os.path.isdir(os.path.join(botparams["watchfolder"], d))]
        inputline = sorted(inputline)
        exist = False
        item = [mod]
        for folder in inputline:
            if folder == item[0]:
                exist = True
        if ((exist != True)):
            slackreply("Parker, the mod folder doesn't exist in the input folder.")
            return None

    #############################################
    #### VALIDATION COMPLETE SO EXEC COMMAND ####
    #############################################

    if operation=="add":
        repojson["requiredMods"].append({"modName":mod,"Enabled":True}
        with open('/repository/storage/'+str(repo)+'repo.json', 'w') as outfile:
            json.dump(repojson, outfile, indent=4)
        return None

    if operation=="remove":
        for i in repojson["requiredMods"]:
            if i["modName"] == mod:
                repojson["requiredMods"].remove(i)
                break
        with open('testrepo.json', 'w') as outfile:
            json.dump(repojson, outfile, indent=4)
        return None
