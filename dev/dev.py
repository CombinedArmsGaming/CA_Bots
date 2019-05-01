import json
repo="test"
repojson=True
repomods=""

with open(str(repo)+'repo.json') as data_file:
    repojson = json.load(data_file)
for x in repojson["requiredMods"]:
    repomods=str(repomods)+str((x["modName"]))+";"

print("The mods in the "+str(repo)+" repo are: "+str(repomods))
