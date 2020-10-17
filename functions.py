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
identifiers = {
"1":  ["mAp2V","NAgrb","Bbm2A","0A5Zn","JbOmn","aVeaV","5VlRA","gnR7V","7b7xA","WAGoA","ObqMb","EAaRn","Xb3Ob","1nXeV","EABGn","6Vw5A"], #World 1
"2":  ["zA0Mn","kb2wA","gb1Kn","AoQzv","MAr3n","QVYRb","JnZ2n","PV4Qb","yb8Pb","gnyrV","MAEoV","qn9JV","lnKkn","MV6DA","1nQen","bmw2n"], #World 2
"3":  ["jnL9V","vAMDb","5AWzb","bdjrn","JbDPb","mnkRA","Ap22V","abx5A","5VJBV","zAvPV","JVPon","ZbjWA","XVzGb","A5QZA","ObNoA","AgXrn"], #World 3
"4":  ["nk2rA","nKv3A","bje7V","b2qZV","VPllV","nyl7A","VY39A","Av89V","bxeQA","AW4kn","bDDrb","nQlOA","nZLOb","n9ZBV","AM8vb","V6BNV"], #World 4
"5":  ["Aa58R","b7l7x","AB1QG","nZLM2","nRM67","b1WmK","AoqEe","b3WOO","AGDKo","nKvxk","nXZMe","A0ZgM","AEOYo","VwMk5","bqYEM","VY3MR"], #World 5
"1c": ["AW7zA","bq7Mn","Aa7RV","Ao2eb","nXLen","Vw85b","V6qDn","nK8kV","b33Ob","A0rMV","nZ32V","VY4Rn","ABDGV","AEBon","b1qKb","n9dJA"], #World 1c
"2c": ["VzoGb","nQOeb","b2WwA","b1p95","AMmDA","VJDBA","AvMPb","bN5oV","bDzPn","bxN5n","nklRV","VPgon","bdarA","bjMWV","nLm9V","V4LQV"], #World 2c
"3c": ["Vezab","Arl3V","b83PV","A5GZV","bqYMb","AGDon","ApQ9n","ApQ2n","AgrJb","bdaqA","Agrrb","b7lxA","bmK2n","Vl5Rb","bOpmA","nRM7A"], #World 3c
"4c": ["b7ljA","bOpaA","Aa5OA","VwMpA","A0ZaV","bqYob","A5GJV","b3WDb","nXZzb","nRM8A","AGD6n","AB19b","Vez1b","bmK9n","AoqpV","Vl5gb"], #World 4c
"5c": ["bx3E5","nLar9","bdaJr","b8zGP","AgrJr","ArdM3","ApQj2","VzJ2G","VJGKB","V45eQ","Av8NP","bNdLo","b2Z5w","nQm4e","V6BRD","VPeKo"], #World 5c
"6":  ["bOeMR","A5XOx","nR5Re","bm2OL","b7WRR","Vl2Wp","VeDY5","AGvLD","AaE79","bqe7e","b3Y34","nXvLa","ABND7","Vwa8y","A0QrO","Aor26"]	 #World 6
}

from level import *

# populate AllLevels with data
with open("level_names.txt", "r") as f:
	level_data = f.read().splitlines()

all_levels = AllLevels()
for i in level_data:
	data = i.split(":")
	all_levels.levels.append(Level(id=data[1],name=data[2],short_name=data[0]))

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
	seconds = seconds % (24 * 3600) 
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60 
	return " • %dh %02dm ago" % (hour, minutes)


def get_level_id(shorthand_levelname):
	global identifiers
	try:
		shorthand_levelname = shorthand_levelname.lower()
		world = shorthand_levelname.split("-")[0] # World?
		level = int(shorthand_levelname.split("-")[1].split("c")[0]) # level?
		challenge = shorthand_levelname.find("c") # Challenge level?
		#print(world, level, 'c' if challenge != -1 else '')
		level_id = identifiers[f"{world}{'c' if challenge != -1 else ''}"][level-1] # get level ID
	except:
		level_id = INVALID_LEVEL_TEXT
	return level_id

def refresh_data(leaderboard_id, override=False):
	global download_url
	current_time = time.time()
	try:
		cache_last_reloaded = os.path.getmtime(f"data/{leaderboard_id}.json")
		
	except FileNotFoundError:
		cache_last_reloaded = 0
		pass
	return cache_last_reloaded


def get_top(level, unbroken=False):
	#refresh_data(leaderboard_id)
	referer = "any"
	if unbroken:
		referer = "unbroken"
	file = level.leaderboard
	leaderboard_data = file[referer]["top1000"]
	formatted = []
	for rank,score in enumerate(leaderboard_data):
		#print(score)
		this_level = {
					"owner":score["owner"],
					"display_name":score["owner"]["display_name"],
					"rank":rank+1,
					"value":score["value"],
					"price":"${:,}".format(score["value"]),
					"didBreak":score["didBreak"]
					}
		formatted.append(this_level)
		if len(formatted) > 1:
			if score["value"] == formatted[rank-1]["value"]: # Allign ranks for scores that tie
				formatted[-1]["rank"] = formatted[rank-1]["rank"]
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
	for c,lvl in enumerate(all_levels.levels):
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
		return int(sanitized_price)
	except:
		return 999999
def get_rank(leaderboard_id, price, unbroken):
	pass

def get_global_leaderboard(unbroken,level_type="all"):
	# level_type = all , regular , challenge
	levels = []
	if level_type == "all":
		loop = 2
	else:
		loop = 1
	for c in range(loop):
		for world in range(5):
			for level in range(16):
				if level_type == "all":
					levels.append(f"{world+1}-{level+1}{('c' if c == 1 else '')}")
				elif level_type == "regular":
					levels.append(f"{world+1}-{level+1}")
				elif level_type == "challenge":
					levels.append(f"{world+1}-{level+1}c")
	if level_type != "challenge":
		for level in range(10): # Only 10 levels in world 6
			levels.append(f"6-{level+1}")
	with open("rank_to_score.txt","r") as rank_to_score:
		rank_to_score = rank_to_score.read().split("\n") # Load rank to points scaling into a list
	leaderboard = {}
	id_to_display_names = {}
	referer = "any"
	if unbroken:
		referer = "unbroken"
	start_score = 100*len(levels)
	for level in levels:
		#print(level)
		#leaderboard_id = get_level_id(level) # get leaderboard id level
		current_board = get_top(all_levels.getByShortName(level), unbroken) # get the leaderboard of level
		for score in current_board:
			if not leaderboard.get(score["owner"]["id"], None):
				id_to_display_names[score["owner"]["id"]] = score["owner"]["display_name"]
				leaderboard[score["owner"]["id"]] = start_score
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

	with open(f"data/global_{level_type}_{unbroken}.json", "w") as f:
		json.dump([leaderboard_with_ranks, id_to_display_names], f)
	return (leaderboard_with_ranks, id_to_display_names)

def load_global(nobreaks, level_type):
	with open(f"data/global_{level_type}_{nobreaks}.json", "r") as f:
		return json.load(f)

def id_from_user(user):
	users = []
	for level in levels:
		level_id = get_level_id(level)
		with open(f"data/{level_id}.json", "r") as f:
			data = json.load(f)
			for entry in data["any"]["top1000"] + data["unbroken"]["top1000"]:
				if entry["owner"] not in users and entry["owner"]["display_name"].lower() == user.lower():
					users.append(entry["owner"])
	return users