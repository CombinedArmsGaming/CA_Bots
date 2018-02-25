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
#### MODLINECOUNTER FOR CONFIDENCE CHECK ####
#############################################

def modlinecount(repo):
    '''Functionality for counting the number of mods in the modline'''
    repofile = repochecker(repo)[0]
    with open(repofile, 'r') as openfile:
        modstring = openfile.readline()
    modline = modstring.split(";")
    modline[:] = [item for item in modline if item]
    modline = set(modline)
    return len(modline)

#############################################
#### REPOSITORY CONSTRUCTOR              ####
#############################################

def repobuilder(action):
    '''This function handles the repository construction'''
    # Sanitise action and print beginning message.
    action = str(action)
    slackreply(("This is Eagle-Six to all units. Message received, "+action+" all repositories in succession. Starting Main Repository now, over. (0/3)"))
    # Ensure that all invlines are generated correctly before startup.
    invlinegen("main")
    invlinegen("ww2")
    invlinegen("test")
    # GENERATE MAIN
    showmanage("main")
    subprocess.call("repogen.sh main "+action, shell=True)
    confirmationmessage("main", "ww2", "1", action)
    # GENERATE WW2
    showmanage("ww2")
    subprocess.call("repogen.sh ww2 "+action, shell=True)
    confirmationmessage("ww2", "test", "2", action)
    # GENERATE TEST
    showmanage("test")
    subprocess.call("repogen.sh test "+action, shell=True)
    confirmationmessage("test", "fin", "3", action)
    # Print confirmation message.
    slackreply(("Eagle-Six to @volc and @klima. Repositories "+action+"d. Eagle-Six out."))

#############################################
#### GENS PROGRESS MESSAGES AS REPO GENS ####
#############################################

def confirmationmessage(repo, nextrepo, count, action):
    '''Formats and prints mid-repository construction updates to Slack'''
    # swifty repo.srf is created at the end of a successful repo generation.
    # We can test for it's existence after a generation attempt to check success.
    # Create repo.srf file path identifier
    checkfile = "/var/www/html/"+repo+"/repo.srf"
    # Check for the repo.srf file, and print the right error message.
    if os.path.isfile(checkfile):
        if nextrepo != "fin":
            slackreply(("This is Eagle-Six. "+repo+" repository "+action+"d ("+(str(modlinecount(repo)))+" mods). Starting "+nextrepo+" Repository ("+(str(modlinecount(nextrepo)))+" mods), over. ("+str(count)+"/3)"))
            return None
        if nextrepo == "fin":
            slackreply(("This is Eagle-Six. "+repo+" repository "+action+"d ("+(str(modlinecount(repo)))+" mods). ("+str(count)+"/3)"))
            return None
    # Print error message if repo.srf doesn't exist.
    slackreply(("There was a problem building "+repo+"repository. @volc should check the console output."))
    return None

#############################################
#### CHECKS FOR REPO AND RETNS FILENAMES ####
#############################################

def repochecker(repo):
    '''Checks if a repository exists and returns the locations of the relevant config files'''
    if repo == "main":
        repofile = repoparams[0]["repofile"]
        invfile = repoparams[0]["invfile"]
    if repo == "ww2":
        repofile = repoparams[1]["repofile"]
        invfile = repoparams[1]["invfile"]
    if repo == "test":
        repofile = repoparams[2]["repofile"]
        invfile = repoparams[2]["invfile"]
    if (repo != "main") and (repo != "ww2") and (repo != "test"):
        slackreply("Parker, that repository wasn't recognised. Try again, over.")
        return ["", ""]
    return [repofile, invfile]

#############################################
#### STRING FORMAT FOR MODLINE CHECKING  ####
#############################################

def showmanage(repo):
    '''Formats and prints repository information to slack'''
    # Check which repo file is to be used and sanity checks it.
    repofile = repochecker(repo)[0]
    invfile = repochecker(repo)[1]
    if repofile == "":
        slackreply("Parker, Bannon has made a mistake in that command. Make sure it gets corrected.")
        return None
    # Open files if they exist and load the contents.
    with open(repofile, 'r') as openfile:
        modstring = openfile.readline()
    with open(invfile, 'r') as openfile:
        invstring = openfile.readline()
    # Print the contents of the files.
    slackreply(("Parker. The " + repo + "repository contains these "+str(modlinecount(repo))+" mods: " + modstring))
    slackreply(("And Swifty will ignore these mods: " + invstring))
    return None

#############################################
#### GENS INVERSE MODLINES FOR STORAGE   ####
#############################################

def invlinegen(repo):
    '''Generates inverse modlines for storage and use in swifty scripts'''
    # Prepares variables for use
    modstring = ""
    invstring = ""
    # Sets variables for chosen repository
    repofile = repochecker(repo)[0]
    invfile = repochecker(repo)[1]
    # Reads in an alphabetical list of all possible mod folders to be used for generation
    inputline = [d for d in os.listdir(botparams["watchfolder"]) if os.path.isdir(os.path.join(botparams["watchfolder"], d))]
    inputline = sorted(inputline)
    # Reads in all the mods in the chosen modline and seperates them into a list
    with open(repofile, 'r') as openfile:
        modstring = openfile.readline()
    modline = modstring.split(";")
    # Generates invline by comparing inputline to modline
    invline = [item for item in inputline if item not in modline]
    # Generates invline string from list
    for mod in invline:
        invstring = (invstring + str(mod)+ ";")
    # Writes invline string to file
    filewriter(invfile, invstring)

#############################################
#### EXEC EDIT OPERATIONS ON THE MODLINE ####
#############################################

def modlinemanage(operation, mod, repo):
    '''Manages the modline addtion/removal operations'''
    # Sets variables for chosen repository
    repofile = repochecker(repo)[0]

    ### SANITY CHECKS ###
    inputline = [d for d in os.listdir(botparams["watchfolder"]) if os.path.isdir(os.path.join(botparams["watchfolder"], d))]
    inputline = sorted(inputline)
    exist = False
    item = [mod]
    for folder in inputline:
        if folder == item[0]:
            exist = True

    # Exit if no repo is selected by repochecker,
    # the mod doesn't begin with an @, or the modfolder doesn't exist in the upload folder.
    # As anything can be used for an update command,
    # ignore the tests for folder existing and
    # beginning with an @ if the command is to do an update.
    if ((repofile == "") or (exist != True) or (item[0][:1] != "@")) and ((operation != "update") or (repofile == "")):
        slackreply("Parker, Bannon has made a mistake in the above command. Make sure it gets corrected. Perhaps the mod folder hasn't been uploaded or the syntax is wrong.")
        return None

    # Reads in all the mods in the chosen modline and seperates them into a list
    with open(repofile, 'r') as openfile:
        modstring = openfile.readline()
    modline = modstring.split(";")

    # IF tree for operation determination
    if operation == "add":
        # Appends mod to active list, removes blank entries,
        # checks for duplicates and then sorts alphabetically.
        modline.append(mod)
        modline[:] = [item for item in modline if item]
        modline = set(modline)
        modline = sorted(modline)
        # Prepares modstring for use, and generates modstring from list.
        modstring = ""
        for mods in modline:
            modstring = (modstring + str(mods)+ ";")
        # Writes modstring to file.
        filewriter(repofile, modstring)
        # Generates invline file from newly updated modline.
        invlinegen(str(repo))
        # ...and tells you what it's done.
        slackreply(("Added " + mod + " to " + repo + " modline, over. (now "+(str(modlinecount(repo)))+" mods)"))
    if operation == "remove":
        # Generates new modline by regenerating modline and omitting mods that match the one being removed.
        gen = [mod]
        modline = [item for item in modline if item not in gen]
        # Removes duplicate mods and sorts alphabetically.
        modline[:] = [item for item in modline if item]
        modline = sorted(modline)
        # Prepares modstring for use, and generates new modfile string.
        modstring = ""
        for mods in modline:
            modstring = (modstring + str(mods)+ ";")
        # Writes modline string to file.
        filewriter(repofile, modstring)
        # Generates invline from newly generated modline.
        invlinegen(str(repo))
        # Then tells everyone it's a clever boy.
        slackreply(("Removed " + mod + " from " + repo + " modline, over. (now "+(str(modlinecount(repo)))+" mods)"))
    if operation == "update":
        # Doesn't give a damn, just generates an invline.
        invlinegen(str(repo))
        # Tells you it's done it.
        slackreply(("Updated " + repo + " modline, over."))
    if (operation != "add") and (operation != "remove") and (operation != "update"):
        # Chastises you for being silly
        slackreply("Parker, I need to know what to do to the modline. Try telling me to add remove or update the modline.")
        return None
    return None
