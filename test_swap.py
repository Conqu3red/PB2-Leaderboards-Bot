from functions import *
import sys
level = sys.argv[1]
if len(sys.argv) > 2:
	path = sys.argv[2]
else:
	path = ""
level_id = all_levels.getByShortName(level).id
print(level_id)

with open(f"{path}/oldest_data_{level}.json") as f:
	old_data = json.load(f)

with open(f"data/{level_id}.json", "r") as f:
	data = json.load(f)

data["any"]["top_history"] = old_data["any"]
data["unbroken"]["top_history"] = old_data["unbroken"]

with open(f"data/{level_id}.json", "w") as f:
	json.dump(data, f)
