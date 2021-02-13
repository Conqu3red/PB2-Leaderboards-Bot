import json, datetime, sys
from copy import deepcopy
with open("data/mAp2V.json", "r") as f:
    data = json.load(f)
if len(sys.argv) > 1 and sys.argv[1] == "cheat":
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(now, "%d/%m/%Y-%H:%M")
    data["any"]["top_history"] = [data["any"]["top_history"][0]]
    top_25_with_cheated = deepcopy(data["any"]["top_history"][0]["data"])
    top_25_with_cheated.insert(0,
    [{"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1}]
    )
    top_25_with_cheated.pop()
    data["any"]["top_history"].append({"time":timestamp, "data": top_25_with_cheated})
    
    data["any"]["top1000"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1})

for history_entry in data["any"]["top_history"]:
    print(history_entry["time"])
    for i in range(0,3):
        for score in history_entry["data"][i]:
            print(f"\t{i+1} - {score['value']} {score['owner']['display_name']}")
if len(sys.argv) > 1 and sys.argv[1] == "cheat":
    with open("data/mAp2V.json", "w") as f:
        json.dump(data, f)