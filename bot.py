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


# Initiate CacheManager.py thread

from CacheManager import *
_thread.start_new_thread(CacheManager, ())


#print(os.path.getmtime("data/collated.json"))
#print(time.time())
weekly_url = "https://dfp529wcvahka.cloudfront.net/manifests/weeklyChallenges.json"
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"
identifiers = {
"1":  ["mAp2V","NAgrb","Bbm2A","0A5Zn","JbOmn","aVeaV","5VlRA","gnR7V","7b7xA","WAGoA","ObqMb","EAaRn","Xb3Ob","1nXeV","EABGn","6Vw5A"], #World 1
"2":  ["zA0Mn","kb2wA","gb1Kn","ZAoeV","MAr3n","QVYRb","JnZ2n","PV4Qb","yb8Pb","gnyrV","MAEoV","qn9JV","lnKkn","MV6DA","1nQen","bmw2n"], #World 2
"3":  ["jnL9V","vAMDb","5AWzb","bdjrn","JbDPb","mnkRA","Ap22V","abx5A","5VJBV","zAvPV","JVPon","ZbjWA","XVzGb","A5QZA","ObNoA","AgXrn"], #World 3
"4":  ["nk2rA","nKv3A","bje7V","b2qZV","VPllV","nyl7A","VY39A","Av89V","bxeQA","AW4kn","bDDrb","nQlOA","nZLOb","n9ZBV","AM8vb","V6BNV"], #World 4
"5":  ["AGDKo","nRM67","AoqEe","bqYEM","b7l7x","Aa58R","b3WOO","VwMk5","AB1QG","nXZMe","A0ZgM","AEOYo","b1WmK","nKvxk","VY3MR","nZLM2"], #World 5
"1c": ["AW7zA","bq7Mn","Aa7RV","Ao2eb","nXLen","Vw85b","V6qDn","nK8kV","b33Ob","A0rMV","nZ32V","VY4Rn","ABDGV","AEBon","b1qKb","n9dJA"], #World 1c
"2c": ["VzoGb","nQOeb","b2WwA","nyXrA","AMmDA","VJDBA","AvMPb","bN5oV","bDzPn","bxN5n","nklRV","VPgon","bdarA","bjMWV","nLm9V","V4LQV"], #World 2c
"3c": ["Vezab","Arl3V","b83PV","A5GZV","bqYMb","AGDon","ApQ9n","ApQ2n","AgrJb","bdaqA","Agrrb","b7lxA","bmK2n","Vl5Rb","bOpmA","nRM7A"], #World 3c
"4c": ["b7ljA","bOpaA","Aa5OA","VwMpA","A0ZaV","bqYob","A5GJV","b3WDb","nXZzb","nRM8A","AGD6n","AB19b","Vez1b","bmK9n","AoqpV","Vl5gb"], #World 4c
"5c": ["VJGKB","AgrJr","ApQj2","V6BRD","nLar9","bx3E5","VzJ2G","nQm4e","bdaJr","Av8NP","bNdLo","b2Z5w","ArdM3","V45eQ","VPeKo","b8zGP"], #World 5c
"6":  ["bOeMR","A5XOx","nR5Re","bm2OL","b7WRR","Vl2Wp","VeDY5","AGvLD","AaE79","bqe7e","b3Y34","nXvLa","ABND7","Vwa8y","A0QrO","Aor26"]	 #World 6
}

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


def get_top(leaderboard_id, unbroken=False):
	refresh_data(leaderboard_id)
	referer = "any"
	if unbroken:
		referer = "unbroken"
	with open(f"data/{leaderboard_id}.json", "r") as file:
		file = json.load(file)
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

def find_user(leaderboard_id, user, unbroken=False):
	refresh_data(leaderboard_id)
	referer = "any"
	if unbroken:
		referer = "unbroken"
	with open(f"data/{leaderboard_id}.json", "r") as file:
		file = json.load(file)
		leaderboard_data = file[referer]["top1000"]
		formatted = []
		for rank,score in enumerate(leaderboard_data):
			if score["owner"]["display_name"] == user:
				formatted = [rank+1,"yes" if score["didBreak"] else "no",score["owner"]["display_name"],"${:,}".format(score["value"])]
		if formatted == []:
			formatted = NOT_TOP1000_TEXT
		return formatted


def create_profile(user, unbroken):
	referer = "any"
	if unbroken:
		referer = "unbroken"
	global levels
	generated = []
	for level in levels:
		#print(level)
		leaderboard_id = get_level_id(level)
		refresh_data(leaderboard_id)
		#print(leaderboard_id)
		with open(f"data/{leaderboard_id}.json", "r") as file:
			file = json.load(file)
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
				if score["owner"]["display_name"] == user:
					found = True
					this_level = {
								"owner":user,
								"level":level,
								"rank":r+1,
								"price":"${:,}".format(score["value"]),
								"didBreak":score["didBreak"],
								"found":True
								}
				prev = score
			if not found:
				this_level = {
							"owner":user,
							"level":level,
							"found":False
							}
			generated.append(this_level)
			#print(this_level)
	#print(joined)
	return generated


levels = []
world = 0
for c in range(2):
	for world in range(5):
		for level in range(16):
			levels.append(f"{world+1}-{level+1}{'c' if c == 1 else ''}")
for level in range(10): # Only 10 levels in world 6
	levels.append(f"6-{level+1}")
#print(levels)



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
	for c,lvl in enumerate(levels):
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


def get_milestones(leaderboard_id, unbroken):
	refresh_bucket_collated()
	percents = [1, 2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50]
	referer = "any"
	if unbroken:
		referer = "unbroken"
	milestones = []
	with open(f"data/collated.json", "r") as file:
		file = json.load(file)
		for c,percentile in enumerate(file[leaderboard_id][referer]):
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
	for level in levels:
		#print(level)
		leaderboard_id = get_level_id(level) # get leaderboard id level
		current_board = get_top(leaderboard_id, unbroken) # get the leaderboard of level
		for score in current_board:
			if score["owner"]["id"] not in leaderboard.keys():
				leaderboard[score["owner"]["id"]] = 100*len(levels)
				id_to_display_names[score["owner"]["id"]] = score["owner"]["display_name"]
			leaderboard[score["owner"]["id"]] += int(rank_to_score[score["rank"]])-100

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
	
	return (leaderboard_with_ranks, id_to_display_names)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

@flags.add_flag("--unbreaking", type=bool, default=False)
@flags.add_flag("--position", type=int, default=0)
@flags.add_flag("--user", type=str)
@flags.add_flag("--price")

@flags.command(name='leaderboard', pass_context=True,aliases=["lb"],help='Get top leaderboard for a level\n ADD DOCUMENTATION HERE')

async def leaderboard(ctx, level, **flags):

	error = {"occurred":False,"detail":""}
	#flags["position"] += -1
	if flags["position"] < 0 or flags["position"] > 1000-NUMBER_TO_SHOW_TOP:
		flags["position"] = 0
	offset = flags["position"]
	level_id = get_level_id(level)
	
	if level_id != INVALID_LEVEL_TEXT: # Top command

		lb = get_top(level_id, flags["unbreaking"])
		if flags["user"] != None and flags["price"] == None and flags["position"] == 0: # Position Command
			for pos,score in enumerate(lb):
				if score['display_name'] == flags["user"]:
					offset = pos
					break
		elif flags["price"] != None and flags["position"] == 0 and flags["user"] == None:
			price = parse_price_input(flags["price"])
			offset = 0
			prev = 0
			for c,entry in enumerate(lb):
				if prev <= price and entry["value"] >= price:
					offset = c
					break
				prev = entry["value"]
		else: # Calculate offset based on passed position and ties
			prev = 0
			for c,entry in enumerate(lb):
				if prev <= offset and entry["rank"] >= offset:
					offset = c
					break
				if entry["rank"] != prev:
					prev = entry["rank"]
		pages = menus.MenuPages(source=GeneralLeaderboardViewer(lb,level,offset,flags["unbreaking"], datetime.datetime.utcfromtimestamp(refresh_data(level_id))), clear_reactions_after=True)
		await pages.start(ctx)
	else:
		error["occurred"] = True
		error["detail"] = INVALID_LEVEL_TEXT
	if error["occurred"]:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			description=error["detail"],
			colour=discord.Colour(0xff0000),
		)
		await ctx.send(
			embed=embed
		)
	
bot.add_command(leaderboard)


class GeneralLeaderboardViewer(menus.ListPageSource):
	def __init__(self, data, level, offset, unbreaking, reload_time, is_weekly_challenge=False, thumbnail_url=None):
		super().__init__(data, per_page=NUMBER_TO_SHOW_TOP)
		self.level = level
		self.offs = offset
		self.unbreaking = unbreaking
		self.data = data
		self.reload_time = reload_time
		self.first = True
		self.is_weekly_challenge = is_weekly_challenge
		self.thumbnail_url = thumbnail_url
		# DOES NOT APPLY OFFSET!
	async def format_page(self, menu, entries): # Entries is already a specific place
		if self.first:
			self.first = False
			menu.current_page = math.floor(self.offs/NUMBER_TO_SHOW_TOP)
			entries = self.data[(self.offs - self.offs % NUMBER_TO_SHOW_TOP):(self.offs - self.offs % NUMBER_TO_SHOW_TOP)+NUMBER_TO_SHOW_TOP]
		
		offset = (menu.current_page * self.per_page) + self.offs
		embed = discord.Embed(
			title=f"Leaderboard for {self.level} {'(Unbreaking)' if self.unbreaking else ''}",
			colour=discord.Colour(0x3b12ef),
			timestamp=self.reload_time # or any other datetime type format.
		)
		if self.is_weekly_challenge and self.thumbnail_url != None:
			embed.set_thumbnail(
				url=self.thumbnail_url
			)
		embed.set_footer(
			text=f"cached leaderboards for {self.level} last updated",
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
		)
		for entry in entries:
			embed.add_field(
				name=f"{entry['rank']}: {entry['display_name']}",
				value=f"{entry['price']} {'(Breaks)' if entry['didBreak'] else ''}", # no breaking, so we don't say it broke
				inline=True
			)
		#return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))
		return embed


@flags.add_flag("--unbreaking", type=bool, default=False)
@flags.command(name='profile',help='Get the score of a user on every level.')
async def profile(ctx, user, **flags):
	nobreaks = flags["unbreaking"]
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Processing Data...",
			colour=discord.Colour(0x3b12ef)
			)
		)
	profile_temp = create_profile(user, nobreaks)
	profile = [k for k in profile_temp[:8]] + profile_temp # add 8 filler entries for the stats page
	# find users positions on global leaderboards:
	global_positions = {}
	for level_type in ["all","regular","challenge"]:
		global_leaderboard,id_to_display_names = get_global_leaderboard(nobreaks,level_type)
		if user != None:
				for pos,itm in enumerate(list(global_leaderboard.items())):
					if id_to_display_names[itm[0]] == user:
						global_positions[level_type] = itm[1]
						break
	await message.delete()
	pages = menus.MenuPages(source=ProfileViewer(profile,flags["unbreaking"],global_positions), clear_reactions_after=True)
	await pages.start(ctx)

bot.add_command(profile)

class ProfileViewer(menus.ListPageSource):
	def __init__(self, data, unbreaking, global_positions):
		self.data = data[8:]
		self.unbreaking = unbreaking
		self.global_positions = global_positions
		super().__init__(data, per_page=8)

	async def format_page(self, menu, entries):
		offset = menu.current_page * self.per_page
		
		if menu.current_page == 0:
			embed = discord.Embed(
				title=f"Profile for: {entries[0]['owner']}{' (Unbreaking)' if self.unbreaking else ''}{' (Stats)' if menu.current_page == 0 else ''}",
				description="Showing Stats page. Press :arrow_forward: in reactions to see scores for each level.",
				colour=discord.Colour(0x3b12ef),
				timestamp=datetime.datetime.now() # or any other datetime type format.
			)
			embed.set_author(
				name="PB2 Leaderboards Bot", 
				icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
			)
			global_pos_formatted = f""
			for global_score in self.global_positions.items():
				global_pos_formatted += f"{global_score[0]}: #{global_score[1]['rank']+1} ({global_score[1]['score']})\n"
			if len(global_pos_formatted) != 0:
				embed.add_field(
						name=f"Global Leaderboard Positions",
						value=f"```{global_pos_formatted}```",
						inline=False
				)
			number_top = {"1":0, "10":0, "100":0, "1000":0}
			for element in self.data:
				if element["found"]:
					for category in number_top.keys():
						if element["rank"] <= int(category):
							number_top[category] += 1
			for itm in number_top.items():
				embed.add_field(
					name=f"Top {itm[0]}s",
					value=f"`{itm[1]}`",
					inline=True
				)
		else:
			embed = discord.Embed(
				title=f"Profile for: {entries[0]['owner']}{' (Unbreaking)' if self.unbreaking else ''} {'(Stats)' if menu.current_page == 0 else ''}",
				colour=discord.Colour(0x3b12ef),
				timestamp=datetime.datetime.now() # or any other datetime type format.
			)
			#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
			embed.set_author(
				name="PB2 Leaderboards Bot", 
				icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
			)
			for c, result in enumerate(entries, start=offset):
				if result["found"]:
					embed.add_field(
						name=f"{result['level']}: #{result['rank']}",
						value=f"{result['price']} {'(Breaks)' if result['didBreak'] else ''}", # no breaking, so we don't say it broke
						inline=True
					)
				elif not result["found"]:
					embed.add_field(
						name=f"{result['level']}:",
						value=f"❌",
						inline=True
					)
		return embed


@flags.add_flag("--unbreaking", type=bool, default=False)
@flags.command(name='milestones',help='Get Milestones for a given level')
async def milestones(ctx, level, **flags):
	nobreaks = flags["unbreaking"]
	level_id = get_level_id(level)
	milestones = get_milestones(level_id, nobreaks)
	embed = discord.Embed(
		title=f"Milestones for {level} {'(Unbreaking)' if nobreaks else ''}",
		colour=discord.Colour(0x3b12ef),
		timestamp=datetime.datetime.utcfromtimestamp(refresh_bucket_collated()) # or any other datetime type format.
	)
	#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
	)
	embed.set_footer(
		text=f"Milestone cache last updated",
	)

	for milestone in milestones:
		if milestone != None:
			startValue = "${:,}".format(milestone["startValue"])
			endValue = "${:,}".format(milestone["endValue"])
			embed.add_field(
				name=f"Top {milestone['percent']}%",
				value=f"Above #{milestone['endRank']} ({endValue})",
				inline=True
			)
	await ctx.send(
		embed=embed
	)

bot.add_command(milestones)
@flags.add_flag("--unbreaking", type=bool, default=False)
@flags.add_flag("--type", type=str, default="all")
@flags.add_flag("--user", type=str)

@flags.command(name='globaltop',help='Get Global Leaderboard')

async def globaltop(ctx, **flags):
	offset = 0
	level_type = flags["type"]
	nobreaks = flags["unbreaking"]
	level_type = level_type.lower()
	if level_type not in ["all", "regular", "challenge"]:
		level_type = "all"
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Processing Data...",
			colour=discord.Colour(0x3b12ef)
			)
		)
	global_leaderboard,id_to_display_names = get_global_leaderboard(nobreaks,level_type)
	
	if flags["user"] != None:
			for pos,itm in enumerate(list(global_leaderboard.items())):
				if id_to_display_names[itm[0]] == flags["user"]:
					offset = pos
					break
	embed = discord.Embed(
			title=f"Global Leaderboard:",
			colour=discord.Colour(0x3b12ef)
		)
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
	)
	lb = []
	for c,itm in enumerate(list(global_leaderboard.items())):
		lb.append({
				"name":f"{itm[1]['rank']+1}: {id_to_display_names[itm[0]]}",
				"value":f"Score: {itm[1]['score']}",
				"inline":True
		}
		)
		#print(c,id_to_display_names[itm[0]], itm[1])
	await message.delete()
	pages = menus.MenuPages(source=GlobalLeaderboardViewer(lb, offset, level_type, nobreaks), clear_reactions_after=True)
	await pages.start(ctx)


bot.add_command(globaltop)
class GlobalLeaderboardViewer(menus.ListPageSource):
	def __init__(self, data, offset, level_type, unbreaking):
		self.data = data
		self.offs = offset
		self.first = True
		self.level_type = level_type
		self.unbreaking = unbreaking
		super().__init__(data, per_page=12)

	async def format_page(self, menu, entries):
		if self.first:
			self.first = False
			menu.current_page = math.floor(self.offs/NUMBER_TO_SHOW_TOP)
			entries = self.data[(self.offs - self.offs % NUMBER_TO_SHOW_TOP):(self.offs - self.offs % NUMBER_TO_SHOW_TOP)+NUMBER_TO_SHOW_TOP]
		offset = (menu.current_page * self.per_page) + self.offs
		embed = discord.Embed(
			title=f"Global Leaderboard ({self.level_type} levels) {'(Unbreaking)' if self.unbreaking else ''}",
			colour=discord.Colour(0x3b12ef),
			timestamp=datetime.datetime.now() # or any other datetime type format.
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
		)
		for c, result in enumerate(entries, start=offset):
			embed.add_field(
				name=result["name"],
				value=result["value"],
				inline=result["inline"]
			)
		#return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))
		return embed


@flags.add_flag("--week", type=int, default=0)
@flags.add_flag("--unbreaking", type=bool, default=False)
@flags.add_flag("--position", type=int, default=0)
@flags.add_flag("--user", type=str)
@flags.add_flag("--price")
@flags.command(name='weekly',help='Command Not Complete - Don\'t use')
#@commands.cooldown(1, 5, commands.BucketType.user)

async def weeklyChallenge(ctx, **flags):
	challenge_weeks = {}
	week = flags["week"]
	current_time = time.time()
	try:
		cache_last_reloaded = os.path.getmtime(f"data/weeklyChallenges.json")
		
	except FileNotFoundError:
		cache_last_reloaded = 0
		pass
	if current_time - cache_last_reloaded > 28800: # 8 hours
		r = requests.get(weekly_url)
		with open(f"data/weeklyChallenges.json", "wb") as cache_file:
			cache_file.write(r.content)
		print("[CacheManager] Updated weeklyChallenges")
	with open("data/weeklyChallenges.json") as file:
		data = json.load(file)
	

	for item in data:
		challenge_weeks[item["week"]] = item
	
	if week < 1 or week > len(challenge_weeks.values()):
		week = list(challenge_weeks.keys())[-1]
	error = {"occurred":False,"detail":""}
	#flags["position"] += -1
	if flags["position"] < 0 or flags["position"] > 1000-NUMBER_TO_SHOW_TOP:
		flags["position"] = 0
	offset = flags["position"]
	level_id = "WC." + challenge_weeks[week]["id"]
	
	if level_id != INVALID_LEVEL_TEXT: # Top command

		lb = get_top(level_id, flags["unbreaking"])
		if flags["user"] != None and flags["price"] == None and flags["position"] == 0: # Position Command
			for pos,score in enumerate(lb):
				if score['display_name'] == flags["user"]:
					offset = pos
					break
		elif flags["price"] != None and flags["position"] == 0 and flags["user"] == None:
			price = parse_price_input(flags["price"])
			offset = 0
			prev = 0
			for c,entry in enumerate(lb):
				if prev <= price and entry["value"] >= price:
					offset = c
					break
				prev = entry["value"]
		else: # Calculate offset based on passed position and ties
			prev = 0
			for c,entry in enumerate(lb):
				if prev <= offset and entry["rank"] >= offset:
					offset = c
					break
				if entry["rank"] != prev:
					prev = entry["rank"]
		pages = menus.MenuPages(source=GeneralLeaderboardViewer(lb,challenge_weeks[week]["title"],offset,flags["unbreaking"], datetime.datetime.utcfromtimestamp(refresh_data(level_id)), True, challenge_weeks[week]["preview"]), clear_reactions_after=True)
		await pages.start(ctx)
	else:
		error["occurred"] = True
		error["detail"] = INVALID_LEVEL_TEXT
	if error["occurred"]:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			description=error["detail"],
			colour=discord.Colour(0xff0000),
		)
		await ctx.send(
			embed=embed
		)
	



bot.add_command(weeklyChallenge)


@bot.event
async def on_ready():
	print("[Bot] Connected to Discord!")
	#await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Your commands"))


@bot.event
async def on_command_error(ctx, error):

	send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError, flags._parser.ArgumentParsingError)

	if isinstance(error, commands.CommandNotFound):  # fails silently
		#await ctx.send("```Invalid Command.```")
		pass

	elif isinstance(error, send_help):
		_help = await send_cmd_help(ctx)
		await ctx.send(embed=_help)

	elif isinstance(error, commands.CommandOnCooldown):
		await ctx.send(f'This command is on cooldown. Please wait {error.retry_after:.2f}s')

	elif isinstance(error, commands.MissingPermissions):
		await ctx.send('You do not have the permissions to use this command.')
	# If any other error occurs, prints to console.
	else:
		raise error
		pass

async def send_cmd_help(ctx):
	cmd = ctx.command
	em = discord.Embed(title=f'Usage: {ctx.prefix}{cmd} {cmd.signature}')
	em.color = discord.Color.green()
	em.description = cmd.help
	return em
 

bot.run(TOKEN)