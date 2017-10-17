import json
from datetime import datetime
import time

teststring = "[A3] Operation Mute Claw | Joint SOF | SUN OCT22 1900 UTC"

testdictionary = {"original":"","game":"","event-title":"","event-desc":"","event-datetime":"","event-host":"","event-url":"","reddit-id":"","discord-id":""}

##### EATS STRINGS #####

testdictionary["original"]=teststring
testdictionary["reddit-id"]="testredditid"
testdictionary["discord-id"]="testdiscordid"
testdictionary["event-host"]="fictionalperson"
testdictionary["event-url"]="http://reddit.com/r/combinedarms/fakepost"

# Identifies game string & enters it
game = teststring.split("]")[:1]
game = (str(game)[3:(len(str(game))-2)])
testdictionary["game"] = game

# Identifies and isolates metadata strings

digester = teststring.split("|")
blanklist = []

stripvalue = len(game)+2
digester[0] = digester[0][stripvalue:]
for unit in digester:
    unit = unit.strip()
    blanklist.append(unit)

testdictionary["event-title"]=blanklist[0]
testdictionary["event-desc"]=blanklist[1]

# Parsing the date into something useful
blanklist[2] = datetime.strptime(blanklist[2][:len(blanklist[2])-4],'%a %b%d %H%M')
# Apply correct year if someone schedules an event early in the next year
blanklist[2] = blanklist[2].replace(year = datetime.now().year)
if(blanklist[2].month < datetime.today().month):
    blanklist[2] = blanklist[2].replace(year = (datetime.now().year+1))

testdictionary["event-datetime"]=str(blanklist[2])

for unit in testdictionary:
    print (unit + " " + testdictionary[str(unit)])
