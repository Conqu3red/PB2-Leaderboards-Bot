import json, datetime, sys
from copy import deepcopy
with open("data/mAp2V.json", "r") as f:
    data = json.load(f)
if len(sys.argv) > 1 and sys.argv[1] == "cheat":
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(now, "%d/%m/%Y-%H:%M")
    data["any"]["top_history"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1, "time":timestamp})
    data["any"]["top1000"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1})

if len(sys.argv) > 1 and sys.argv[1] == "clear":
    data["any"]["top_history"] = []

for score in data["any"]["top_history"]:
        print(f"{score['time']} - {score['value']} {score['owner']['display_name']}")
if len(sys.argv) > 1 and sys.argv[1] in ["cheat", "clear"]:
    with open("data/mAp2V.json", "w") as f:
        json.dump(data, f)