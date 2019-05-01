import json

repojson=True
repomods=[]

with open('testrepo.json') as data_file:
    repojson = json.load(data_file)

for x in repojson["requiredMods"]:
    repomods.append(x["modName"])

print(repomods)

print(repojson["requiredMods"])

for i in repojson["requiredMods"]:
    if i["modName"] == "@ace_ca":
        repojson["requiredMods"].remove(i)
        break

print(repojson["requiredMods"])

with open('testrepo.json', 'w') as outfile:
    json.dump(repojson, outfile, indent=4)
