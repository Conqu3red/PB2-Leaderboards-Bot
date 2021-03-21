import json, datetime, sys
from copy import deepcopy
from optparse import OptionParser

parser = OptionParser(usage='usage: %prog [options]', version='%prog 1.0.0')
parser.add_option('--cheat', default=False, action='store_true', dest='cheat', help='whether to add a cheated score')
parser.add_option('--id', default="mAp2V", type=str, action='store', dest='id', help='id for level')
parser.add_option('--clear', default=False, action='store_true', dest='clear', help='whether to clear the top history for the level')

(options, args) = parser.parse_args()


with open(f"data/{options.id}.json", "r") as f:
    data = json.load(f)
if options.cheat:
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(now, "%d/%m/%Y-%H:%M")
    data["any"]["top_history"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1, "time":timestamp})
    data["any"]["top1000"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1})

if options.cheat:
    data["any"]["top_history"] = []

for score in data["any"]["top_history"]:
        print(f"{score['time']} - {score['value']} {score['owner']['display_name']}")
if options.cheat or options.clear:
    with open("data/mAp2V.json", "w") as f:
        json.dump(data, f)