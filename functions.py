import requests
import _thread
import datetime
import time
import os
import asyncio
import json
import re
import discord
from discord.ext import commands
from discord.ext import menus
from discord.ext import flags
from dotenv import load_dotenv
import math
BUCKET_URL = "https://dfp529wcvahka.cloudfront.net/manifests/leaderboards/buckets/collated.bin"
INVALID_LEVEL_TEXT = "Invalid Level."
NOT_TOP1000_TEXT = "This User is not in the top 1000 for the specified level"
NUMBER_TO_SHOW_TOP = 12

weekly_url = "https://dfp529wcvahka.cloudfront.net/manifests/weeklyChallenges.json"
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"

from level import *

# populate AllLevels with data
with open("level_names.txt", "r") as f:
	level_data = f.read().splitlines()

all_levels = AllLevels()
for i in level_data:
	data = i.split(":")
	all_levels.levels.append(Level(id=data[1].strip(),name=data[2].strip(),short_name=data[0].strip(), budget=float(data[3].strip())))

# populate WeeklyLevels with data
weekly_levels = WeeklyLevels()



levels = []
world = 0
for c in range(2):
	for world in range(5):
		for level in range(16):
			levels.append(f"{world+1}-{level+1}{'c' if c == 1 else ''}")
for level in range(10): # Only 10 levels in world 6
	levels.append(f"6-{level+1}")
#print(levels)

def time_since_reload(t):
	seconds = time.time() - t
	#seconds = seconds % (24 * 3600) 
	#hour = seconds // 3600
	#seconds %= 3600
	#minutes = seconds // 60
	#seconds %= 60 
	#return "%dh %02dm ago" % (hour, minutes)
	return nice_time_format(seconds)


def get_top(level, unbroken=False):
	#refresh_data(leaderboard_id)
	referer = "any"
	if unbroken:
		referer = "unbroken"
	file = level.leaderboard
	leaderboard_data = file[referer]["top1000"]
	formatted = []
	now = time.time()
	for rank,score in enumerate(leaderboard_data):
		#print(score)
		this_level = {
					"owner":score["owner"],
					"display_name":score["owner"]["display_name"],
					"rank":score["rank"],
					"value":score["value"],
					"price":"${:,}".format(score["value"]),
					"didBreak":score["didBreak"],
					"time":score.get("time", now),
					"level_name":level.name,
					"level_short_name":str(level.short_name)
					}
		formatted.append(this_level)
	return formatted


def create_profile(user, unbroken):
	user_id = re.search(r"@\w+", user)
	referer = "any"
	if unbroken:
		referer = "unbroken"
	global levels
	generated = []
	owner = ""
	user_decided = ""
	for level in all_levels.levels + weekly_levels.levels:
		#print(level)
		#leaderboard_id = get_level_id(level)
		#refresh_data(leaderboard_id)
		#print(leaderboard_id)
		
		file = level.leaderboard
		leaderboard_data = file[referer]["top1000"]
		found = False
		tied = 0
		for rank,score in enumerate(leaderboard_data):
			r = rank
			if rank > 0:
				if score["value"] == prev["value"]:
					tied += 1
					r = rank-tied
				else:
					tied = 0
			if (score["owner"]["display_name"].lower() == user.lower()) or (score["owner"]["id"] == user[1:]):
				#print(score, user)
				if not user_decided:
					#print("Set user to", score["owner"])
					user_decided = score["owner"]
				if score["owner"] == user_decided:
					owner = score["owner"]["display_name"]
					found = True
					this_level = {
								"owner": score["owner"]["display_name"],
								"level":level.short_name,
								"rank":r+1,
								"price":"${:,}".format(score["value"]),
								"didBreak":score["didBreak"],
								"found":True
								}
			prev = score
		if not found:
			this_level = {
						"owner":user,
						"level":level.short_name,
						"found":False
						}
		generated.append(this_level)
		#print(this_level)
	#print(joined)
	return generated, owner






def refresh_bucket_collated(override=False):
	global BUCKET_URL
	current_time = time.time()
	try:
		cache_last_reloaded = os.path.getmtime(f"data/collated.bin")
		
	except FileNotFoundError:
		cache_last_reloaded = 0
		pass
	if current_time - cache_last_reloaded > 28800: # 8 hours
		url = BUCKET_URL
		r = requests.get(url)
		with open(f"data/collated.bin", "wb") as cache_file:
			cache_file.write(r.content)
	
	with open("data/collated.bin", "rb") as f:
		bytes_read = f.read()
	
	buckets = {}
	offset = 0
	while offset < len(bytes_read):
		level_id = bytes_read[offset:offset+5].decode("utf-8") 
		#print(offset)
		#print(bytes_read[offset-15:offset+15])
		offset += 5
		#print(level_id)
	
		buckets[level_id] = {}
		if bytes_read[offset:offset+4] not in [b'\xff\xff\xff\xff',b'\x01\x00\x00\x00']:
			continue
		for category in ["any", "unbroken"]:
			buckets[level_id][category] = []
			for i in range(100):
				if bytes_read[offset:offset+4] == b"\xff\xff\xff\xff":
					offset += 4
					continue
				current = {}
				current["startRank"] = int.from_bytes(bytes_read[offset:offset+4], "little")
				offset += 4
				current["endRank"] = int.from_bytes(bytes_read[offset:offset+4], "little")
				offset += 4
				current["startValue"] = int.from_bytes(bytes_read[offset:offset+4], "little")
				offset += 4
				current["endValue"] = int.from_bytes(bytes_read[offset:offset+4], "little")
				offset += 4
				buckets[level_id][category].append(current)
	with open("data/collated.json","w") as file:
		json.dump(buckets, file)
	
	return cache_last_reloaded


def get_milestones(level, unbroken):
	refresh_bucket_collated()
	percents = [1, 2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50]
	referer = "any"
	if unbroken:
		referer = "unbroken"
	milestones = []
	with open(f"data/collated.json", "r") as file:
		file = json.load(file)
		for c,percentile in enumerate(file[level.id][referer]):
			if c+1 in percents:
				current = percentile
				if current != None:
					current["percent"] = c+1
				milestones.append(current)
	return milestones

def parse_price_input(price):
	sanitized_price = ""
	for char in price:
		if char in "1234567890.":
			sanitized_price += char
	try:
		return float(sanitized_price)
	except:
		return 999999
def get_rank(leaderboard_id, price, unbroken):
	pass

def get_global_leaderboard(unbroken,level_type="all", moneyspent=False, worlds=None):
	# level_type = all , regular , challenge
	levels = []
	# parse inputted worlds
	if worlds:
		if worlds.count(",") == 0:
			worlds = [worlds.strip()]
		else:
			worlds = [w.strip() for w in worlds.split(",")]
	else:
		worlds = []
	worlds = list(dict.fromkeys(worlds))
	levels = []
	valid_worlds = set()
	for level in all_levels.levels:
		if not worlds:
			if level.short_name.is_challenge_level and level_type in ["all", "challenge"]: # add challenge levels
				levels.append(level)
			elif not level.short_name.is_challenge_level and level_type in ["all", "regular"]: # regular
				levels.append(level)
		elif worlds:
			for world in worlds:
				if world.replace("c", "") == str(level.short_name.world) and world.endswith("c") == level.short_name.is_challenge_level:
					levels.append(level)
					valid_worlds.add(world)
	worlds = list(valid_worlds)

	for level in weekly_levels.levels:
		if level_type == "weekly":
			levels.append(level)
	with open("rank_to_score.txt","r") as rank_to_score:
		rank_to_score = rank_to_score.read().split("\n") # Load rank to points scaling into a list
	leaderboard = {}
	id_to_display_names = {}
	referer = "any"
	if unbroken:
		referer = "unbroken"
	if moneyspent:
		start_score = sum([level.budget for level in levels])
	else:
		start_score = 100*len(levels)
	for level in levels:
		#print(level)
		#leaderboard_id = get_level_id(level) # get leaderboard id level
		current_board = get_top(level, unbroken) # get the leaderboard of level
		for score in current_board:
			if not leaderboard.get(score["owner"]["id"], None):
				id_to_display_names[score["owner"]["id"]] = score["owner"]["display_name"]
				leaderboard[score["owner"]["id"]] = start_score
			if moneyspent:
				leaderboard[score["owner"]["id"]] -= (level.budget-score["value"])
			else:
				leaderboard[score["owner"]["id"]] += int(rank_to_score[score["rank"]])-100
			#leaderboard[score["owner"]["id"]] = leaderboard.get(score["owner"]["id"], start_score)+int(rank_to_score[score["rank"]])-100

	leaderboard_sorted = {user_id: score for user_id, score in sorted(leaderboard.items(), key=lambda item: item[1])}
	leaderboard_with_ranks = {}
	for c,item in enumerate(leaderboard_sorted.items()):
		this = {}
		this["score"] = item[1]
		this["rank"] = c
		if c > 0:
			if this["score"] == prev["score"]: # Allign ranks for scores that tie
				this["rank"] = prev["rank"]
		prev = this
		leaderboard_with_ranks[item[0]] = this

	#with open(f"data/global_{level_type}_{unbroken}.json", "w") as f:
	#	json.dump([leaderboard_with_ranks, id_to_display_names], f)
	return leaderboard_with_ranks, id_to_display_names, worlds

def _load_global(nobreaks, level_type="all"):
	with open(f"data/global_{level_type}_{nobreaks}.json", "r") as f:
		return json.load(f)

def get_oldest_scores_leaderboard(unbroken=False):
	referer = "unbroken" if unbroken else "any"
	leaderboard_ranked = []
	for level in all_levels.levels:
		data = level.leaderboard
		scores_for_level = []
		
		lowest_price = min([score["value"] for score in data[referer]["top_history"]])
		scores_for_level = [score for score in data[referer]["top_history"] if score["value"] == lowest_price]
		
		# - split top_history into time brackets (sorted newest to oldest)
		time_brackets = {}
		for score in data[referer]["top_history"]:
			if time_brackets.get(datetime.datetime.strptime(score["time"], "%d/%m/%Y-%H:%M").timestamp()):
				time_brackets[datetime.datetime.strptime(score["time"], "%d/%m/%Y-%H:%M").timestamp()].append(score)
				continue
			time_brackets[datetime.datetime.strptime(score["time"], "%d/%m/%Y-%H:%M").timestamp()] = [score]
		
		for t in time_brackets:
			price = min([score["value"] for score in time_brackets[t]])
			time_brackets[t] = [score for score in time_brackets[t] if score["value"] == price]
		time_brackets = dict(sorted(time_brackets.items(), reverse=True))
		#print(time_brackets)


		# for each #1 user, loop back to check how many scores they have had consecutively #1
		for score in scores_for_level:
			score["level_short_name"] = str(level.short_name)
			all_of_this_users_prices = [s for s in data[referer]["top_history"] if s["owner"]["id"] == score["owner"]["id"]]
			i = 1
			score["time"] = datetime.datetime.strptime(score["time"], "%d/%m/%Y-%H:%M").timestamp()
			if len(all_of_this_users_prices) < 2:
				continue
			
			for t, time_bracket in time_brackets.items():
				found_streak_break = False
				for s in time_bracket: # #1 scores in the bracket
					if s["owner"]["id"] == score["owner"]["id"]:
						score["time"] = t
						i += 1
					if i >= len(all_of_this_users_prices):
						break
					if s["value"] != score["value"] and s["value"] < all_of_this_users_prices[i]:
						found_streak_break = True
				if found_streak_break:
					break
		scores_for_level_without_duplicates = []
		
		# group scores that are "identical"
		for score in scores_for_level:
			identical_score = next(
				(
					i for i,s in enumerate(scores_for_level_without_duplicates) if s["value"] == score["value"] and 
						s["didBreak"] == score["didBreak"] and 
						s["time"] == score["time"]
				), 
				None
			)
			if identical_score != None:
				scores_for_level_without_duplicates[identical_score]["num_players"] = scores_for_level_without_duplicates[identical_score].get("num_players", 1) + 1
			else:
				scores_for_level_without_duplicates.append(score)
		leaderboard_ranked += scores_for_level_without_duplicates
	
	# sort and rank the scores
	leaderboard = list(sorted(leaderboard_ranked, key = lambda item: item["time"]))
	leaderboard_ranked = []
	for c, score in enumerate(leaderboard):
		score["time_rank"] = c+1
		leaderboard_ranked.append(score)
		if len(leaderboard_ranked) > 1:
			if score["time"] == leaderboard_ranked[-2]["time"]:
				leaderboard_ranked[-1]["time_rank"] = leaderboard_ranked[-2]["time_rank"]
	return leaderboard_ranked

def nice_time_format(seconds):
	d = int(seconds // (60*60*24))
	h = int(seconds // (60*60) % 24)
	m = int(seconds // 60 % 60)
	s = int(seconds % 60)
	ret = f""
	if d != 0: ret += f"{d}d "
	if h != 0 and d == 0: ret += f"{h}h "
	if m != 0 and d == 0 and h == 0: ret += f"{m}m "
	if d == 0 and h == 0 and m == 0: ret += f"{s}s "
	return ret + "ago"

def id_from_user(user):
	users = []
	for level in all_levels.levels:
		data = level.leaderboard
		for entry in data["any"]["top1000"] + data["unbroken"]["top1000"]:
			if entry["owner"] not in users and entry["owner"]["display_name"].lower() == user.lower():
				users.append(entry["owner"])
	return users