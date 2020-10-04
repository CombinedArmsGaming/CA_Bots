######  SLACKBOT FOR COMBINED ARMS     ######
######  DEV: CALUM CAMERON BROOKES     ######
######  CALUM.C.BROOKES@GMAIL.COM      ######
######  VER INFO IN MAIN.PY 02/8/2020  ######

'''This module contains all the repository management functions'''

from __future__ import absolute_import
import os
import subprocess
import json
from globalvar import slackreply, botparams, repoparams
from discord import post_discord
from hcsocket import sendtohc

#############################################
#### UPDATES THE HC MODLINES             ####
#############################################

def hcupdater(repo1):
    '''Contacts the HC and updates the repo.'''
    for r in repoparams:
        if r["name"]==str(repo1):
            with open('/repository/storage/'+str(repo1)+'repo.json') as data_file:
                repojson = json.load(data_file)
    repomods=""
    for x in repojson["requiredMods"]:
        repomods=str(repomods)+str((x["modName"]))+";"
    slackreply("Mods sent to HC: "+str(repomods))
    return(sendtohc(command="update",repo=repo1,payload=str(repomods)))

#############################################
#### REPOSITORY CONSTRUCTOR              ####
#############################################

def repobuilder(stealthbool):
    '''This function handles the repository construction'''
    # Sanitise action and print beginning message.
    slackreply(("This is Eagle-Six to all units. Message received, build all repositories in succession, over."))
    for r in repoparams:
        showmods(str(r["name"]))
        subprocess.call("/slackbot/r3pogen.sh "+str(r["name"]), shell=True)
        buildbool = True
        buildbool = confirmationmessage(str(r["name"]))
        if (buildbool == False):
            slackreply("Eagle-Six here, tactical aid is required, the repository did not build correctly. Ending operation.")
            break
    for r in repoparams:
        try:
            hcupdater(str(r["name"]))
        except:
            slackreply("Eagle-Six here, tactical aid is required, cannot confirm HC received repo commandlines. Ending operation.")
            break
    # Print confirmation message.
    slackreply("Eagle-Six to @volc and @klima. Repositories built. Eagle-Six out.")
    if (stealthbool == True):
        post_discord("announcements", "@everyone repositories have been updated.")
    
def reposingle(reponame):
    '''This function handles the repository construction'''
    # Sanitise action and print beginning message.
    slackreply(("This is Eagle-Six to all units. Message received, build a single repository, over."))
    for r in repoparams:
        if str(r["name"]) == str(reponame):
            showmods(str(r["name"]))
            subprocess.call("/slackbot/r3pogen.sh "+str(r["name"]), shell=True)
            buildbool = True
            buildbool = confirmationmessage(str(r["name"]))
            if (buildbool == False):
                slackreply("Eagle-Six here, tactical aid is required, the repository did not build correctly. Ending operation.")
                break
    for r in repoparams:
        if str(r["name"]) == str(reponame):
            try:
                hcupdater(str(r["name"]))
            except:
                slackreply("Eagle-Six here, tactical aid is required, cannot confirm HC received repo commandlines. Ending operation.")
                break
    # Print confirmation message.
    slackreply("Eagle-Six to @volc and @klima. Repository built. Eagle-Six out.")

#############################################
####  GENS ERROR MESSAGES AS REPO GENS   ####
#############################################

def confirmationmessage(repo):
    '''Formats and prints mid-repository construction updates to Slack.'''
    # swifty repo.srf is created at the end of a successful repo generation.
    # We can test for it's existence after a generation attempt to check success.
    # Create repo.json file path identifier
    checkfile = "/var/www/html/"+str(repo)+"/repo.json"
    # Check for the repo.srf file, and print the right error message.
    if not (os.path.isfile(checkfile)):
        # Print error message if repo.json doesn't exist.
        slackreply(("There was a problem building "+repo+"repository. @volc should check the console output."))
        return False
    slackreply("Built "+str(repo)+" repo.")
    return True

#############################################
####  PRINTS MODS IN GIVEN REPO IN SLACK ####
#############################################

def showmods(repo):
    '''Formats and prints repository information to slack'''
    # Check which repo file is to be used and sanity checks it.
    if repochecker(repo) == False:
        slackreply("Parker, that repository doesn't exist, so I can't show you it.")
        return None

    repojson=True
    repomods=""
    for r in repoparams:
        if r["name"]==repo:
            with open('/repository/storage/'+str(repo)+'repo.json') as data_file:
                repojson = json.load(data_file)
    for x in repojson["requiredMods"]:
        repomods=str(repomods)+str((x["modName"]))+";"

    slackreply("The "+str(len(repojson["requiredMods"]))+" mods in the "+str(repo)+" repo are: "+str(repomods))

#############################################
#### CHECKS FOR REPO AND RETURNS BOOLEAN ####
#############################################

def repochecker(repo):
    '''Checks if a repository exists and returns the locations of the relevant config files'''
    for r in repoparams:
        if str(r["name"])==str(repo):
            return True
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
        repojson["requiredMods"].append({"modName":mod,"Enabled":True})
        with open('/repository/storage/'+str(repo)+'repo.json', 'w') as outfile:
            json.dump(repojson, outfile, indent=4)
        slackreply("Parker, I've added "+str(mod)+" to the "+str(repo)+" repo.")
        return None

    if operation=="remove":
        for i in repojson["requiredMods"]:
            if str(i["modName"]) ==str(mod):
                repojson["requiredMods"].remove(i)
                break
        with open('/repository/storage/'+str(repo)+'repo.json', 'w') as outfile:
            json.dump(repojson, outfile, indent=4)
        slackreply("Parker, I've removed "+str(mod)+" from the "+str(repo)+" repo.")
        return None
