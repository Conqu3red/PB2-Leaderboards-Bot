from functions import create_time_brackets
import json, datetime, sys
from copy import deepcopy
from optparse import OptionParser

parser = OptionParser(usage='usage: %prog [options]', version='%prog 1.0.0')
parser.add_option('--cheat', default=False, action='store_true', dest='cheat', help='whether to add a cheated score')
parser.add_option('--id', default="mAp2V", type=str, action='store', dest='id', help='id for level')
parser.add_option('--clear', default=False, action='store_true', dest='clear', help='whether to clear the top history for the level')
parser.add_option("--unbreaking", default=False, action='store_true', dest='unbreaking', help='display unbreaking or not')

(options, args) = parser.parse_args()

referer = "unbroken" if options.unbreaking else "any"

with open(f"data/{options.id}.json", "r", encoding="utf-8") as f:
	data = json.load(f)
if options.cheat:
	now = datetime.datetime.now()
	timestamp = datetime.datetime.strftime(now, "%d/%m/%Y-%H:%M")
	data[referer]["top_history"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1, "time":timestamp})
	data[referer]["top1000"].insert(0, {"id": "aaaaa", "owner": {"id": "aaaaa", "display_name": "testUser"}, "value": 0, "didBreak": True, "rank": 1})

if options.clear:
	data[referer]["top_history"] = []

for score in data[referer]["top_history"]:
	print(f"{score['time']} - {score['value']} {score['owner']['display_name']}")

print()
brackets = create_time_brackets(data[referer])
for time, scores in brackets.items():
	time = datetime.datetime.fromtimestamp(time)
	print(f"\n{time.strftime('%d/%m/%Y-%H:%M')} --------------------------")
	for s in scores:
		print(f"\t\t\t{s['value']} {s['owner']['display_name']}")

if options.cheat or options.clear:
	with open("data/mAp2V.json", "w") as f:
		json.dump(data, f)