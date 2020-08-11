import requests
import _thread
import datetime
import time
import os
import asyncio
import json
import re
import discord
from tabulate import tabulate
from discord.ext import commands
from discord.ext import menus
from discord.ext import flags
from dotenv import load_dotenv
BUCKET_URL = "https://dfp529wcvahka.cloudfront.net/manifests/leaderboards/buckets/collated.json"
INVALID_LEVEL_TEXT = "Invalid Level."
NOT_TOP1000_TEXT = "This User is not in the top 1000 for the specified level"
NUMBER_TO_SHOW_TOP = 12


# Initiate CacheManager.py thread

from CacheManager import *

_thread.start_new_thread( CacheManager, ())


#print(os.path.getmtime("data/collated.json"))
#print(time.time())
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"
identifiers = {
"1": ["mAp2V", "NAgrb", "Bbm2A", "0A5Zn", "JbOmn", "aVeaV", "5VlRA", "gnR7V", "7b7xA", "WAGoA", "ObqMb", "EAaRn", "Xb3Ob", "1nXeV", "EABGn", "6Vw5A"],	#World 1
"2": ["zA0Mn", "kb2wA", "gb1Kn", "ZAoeV", "MAr3n", "QVYRb", "JnZ2n", "PV4Qb", "yb8Pb", "gnyrV", "MAEoV", "qn9JV", "5AWzb", "MV6DA", "1nQen", "bmw2n"],	#World 2
"3": ["jnL9V", "vAMDb", "lnKkn", "bdjrn", "JbDPb", "mnkRA", "Ap22V", "abx5A", "5VJBV", "zAvPV", "JVPon", "ZbjWA", "XVzGb", "A5QZA", "ObNoA", "AgXrn"],	#World 3
"4": ["nk2rA", "nKv3A", "bje7V", "b2qZV", "VPllV", "nyl7A", "VY39A", "Av89V", "bxeQA", "AW4kn", "bDDrb", "nQlOA", "nZLOb", "n9ZBV", "AM8vb", "V6BNV"],	#World 4
"5": ["AGDKo","nRM67","AoqEe","bqYEM","b7l7x","Aa58R","b3WOO","VwMk5","AB1QG","nXZMe","A0ZgM","AEOYo","b1WmK","nKvxk","VY3MR","nZLM2"],	#World 5 :)
"1c": ["AW7zA", "bq7Mn", "Aa7RV", "Ao2eb", "nXLen", "Vw85b", "V6qDn", "nK8kV", "b33Ob", "A0rMV", "nZ32V", "VY4Rn", "ABDGV", "AEBon", "b1qKb", "n9dJA"],   #World 1c
"2c": ["VzoGb", "nQOeb", "b2WwA", "nyXrA", "AMmDA", "VJDBA", "AvMPb", "bN5oV", "bDzPn", "bxN5n", "nklRV", "VPgon", "b83PV", "bjMWV", "nLm9V", "V4LQV"],   #World 2c
"3c": ["Vezab", "Arl3V", "bdarA", "A5GZV", "bqYMb", "AGDon", "ApQ9n", "ApQ2n", "AgrJb", "bdaqA", "Agrrb", "b7lxA", "bmK2n", "Vl5Rb", "bOpmA", "nRM7A"],   #World 3c
"4c": ["b7ljA", "bOpaA", "Aa5OA", "VwMpA", "A0ZaV", "bqYob", "A5GJV", "b3WDb", "nXZzb", "nRM8A", "AGD6n", "AB19b", "Vez1b", "bmK9n", "AoqpV", "Vl5gb"],   #World 4c
"5c": ["VJGKB","AgrJr","ApQj2","V6BRD","nLar9","bx3E5","VzJ2G","nQm4e","bdaJr","Av8NP","bNdLo","b2Z5w","ArdM3","V45eQ","VPeKo","b8zGP"],   #World 5c :)
"6": ["bOeMR","A5XOx","nR5Re","bm2OL","b7WRR","Vl2Wp","VeDY5","AGvLD","AaE79","bqe7e", 'b3Y34', 'nXvLa', 'ABND7', 'Vwa8y', 'A0QrO', 'Aor26']	#Secret World :)
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
		#if formatted != []:
			#table = tabulate(formatted, headers=["Rank","Breaks?","Name", "Price"],tablefmt="pipe")
			#print(table)
		if formatted == []:
			formatted = NOT_TOP1000_TEXT
		return formatted








def create_profile(user, unbroken):
	referer = "any"
	if unbroken:
		referer = "unbroken"
	global levels
	#for level in levels:
	#	get_level_id(level)
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
			for rank,score in enumerate(leaderboard_data):
				if score["owner"]["display_name"] == user:
					found = True
					this_level = {
								"owner":user,
								"level":level,
								"rank":rank+1,
								"price":"${:,}".format(score["value"]),
								"didBreak":score["didBreak"],
								"found":True
								}
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
		cache_last_reloaded = os.path.getmtime(f"data/collated.json")
		
	except FileNotFoundError:
		cache_last_reloaded = 0
		pass
	if current_time - cache_last_reloaded > 28800 or override: # 8 hours
		url = BUCKET_URL
		r = requests.get(url)
		with open(f"data/collated.json", "wb") as cache_file:
			cache_file.write(r.content)
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

	leaderboard_sorted = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1])}
	return (leaderboard_sorted, id_to_display_names)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

@flags.add_flag("--unbreaking", type=bool, default=False)
@flags.add_flag("--position", type=int, default=0)
@flags.add_flag("--user", type=str)
@flags.add_flag("--price")

@flags.command(name='leaderboard', pass_context=True,aliases=["lb"],help='Get top leaderboard for a level\nAppend nobreaks to remove results with breaks')

async def leaderboard(ctx, level, **flags):

	error = {"occurred":False,"detail":""}
	#flags["position"] += -1
	if flags["position"] < 0 or flags["position"] > 1000-NUMBER_TO_SHOW_TOP:
		flags["position"] = 0
	offset = flags["position"]
	level_id = get_level_id(level)
	if flags["user"] != None: # Position Command
		await position(ctx, level, **flags)
	
	elif level_id != INVALID_LEVEL_TEXT: # Top command
		lb = get_top(level_id, flags["unbreaking"])

		if flags["price"] != None and flags["position"] == 0:
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
		embed = discord.Embed(
			title=f"Leaderboard for {level}:",
			colour=discord.Colour(0x3b12ef),
			timestamp=datetime.datetime.utcfromtimestamp(refresh_data(level_id)) # or any other datetime type format.
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
		)
		embed.set_footer(
			text=f"cached leaderboards for {level} last updated",
		)
		
		for entry in lb[offset:offset+NUMBER_TO_SHOW_TOP]:
			embed.add_field(
				name=f"{entry['rank']}: {entry['display_name']}",
				value=f"{entry['price']} {'(Breaks)' if entry['didBreak'] else ''}", # no breaking, so we don't say it broke
				inline=True
			)
	else:
		error["occurred"] = True
		error["detail"] = INVALID_LEVEL_TEXT
	if error["occurred"]:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			colour=discord.Colour(0xff0000),
		)
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
		)
		embed.add_field(
				name=f"Please see below for error info:",
				value=error["detail"],
				inline=True
			)
	await ctx.send(
		embed=embed
	)
bot.add_command(leaderboard)

#@bot.command(name='position', pass_context=True,help='Get the position of a specific user on a certain level')

async def position(ctx, level, **flags):
	nobreaks = flags["unbreaking"]
	user = flags["user"]
	error = {"occurred":False,"detail":""}
	level_id = get_level_id(level)
	embed = discord.Embed(
		title=f"{level}: {user}",
		colour=discord.Colour(0x3b12ef),
		timestamp=datetime.datetime.utcfromtimestamp(refresh_data(level_id)) # or any other datetime type format.
	)
	#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
	)
	embed.set_footer(
		text=f"cached leaderboards for {level} last updated",
	)
	if level_id != INVALID_LEVEL_TEXT:
		lb = find_user(level_id, user, nobreaks)
		
		if lb != NOT_TOP1000_TEXT:
			
			embed.add_field(
				name=f"{lb[0]}: {lb[2]}",
				value=f"{lb[3]} {'(Breaks)' if lb[1] == 'yes' else ''}", # no breaking, so we don't say it broke
				inline=True
			)
			
		else:
			error["occurred"] = True
			error["detail"] = NOT_TOP1000_TEXT
	else:
		error["occurred"] = True
		error["detail"] = INVALID_LEVEL_TEXT
	if error["occurred"]:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			colour=discord.Colour(0xff0000),
		)
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/720412997226332271.png"
		)
		embed.add_field(
				name=f"Please see below for error info:",
				value=error["detail"],
				inline=True
			)
	await ctx.send(
		embed=embed
	)
@bot.command(name='profile',help='Get Profile of a user - may take a while!')
async def profile(ctx, user, unbreaking="no"):
	nobreaks = False
	if unbreaking.lower() in ["nobreaks", "yes"]:
		nobreaks = True
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Downloading Leaderboards... This May take a while",
			colour=discord.Colour(0x3b12ef)
			)
		)
	profile = create_profile(user, nobreaks)
	await message.delete()
	pages = menus.MenuPages(source=ProfileViewer(profile), clear_reactions_after=True)
	await pages.start(ctx)


class ProfileViewer(menus.ListPageSource):
	def __init__(self, data):
		super().__init__(data, per_page=8)

	async def format_page(self, menu, entries):
		offset = menu.current_page * self.per_page
		embed = discord.Embed(
			title=f"Profile for: {entries[0]['owner']}",
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
		#return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))
		return embed



@bot.command(name='milestones',help='Get Milestones for a given level')
async def milestones(ctx, level, unbreaking="no"):
	nobreaks = False
	if unbreaking.lower() in ["nobreaks", "yes"]:
		nobreaks = True
	level_id = get_level_id(level)
	milestones = get_milestones(level_id, nobreaks)
	embed = discord.Embed(
		title=f"Milestones for {level}",
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

@bot.command(name='globaltop',help='Get Global Leaderboard')
async def globaltop(ctx, level_type="all", unbreaking="no"):
	nobreaks = False
	if unbreaking.lower() in ["nobreaks", "yes"]:
		nobreaks = True
	level_type = level_type.lower()
	if level_type not in ["all", "regular", "challenge"]:
		level_type = "all"
	nobreaks = False
	if unbreaking.lower() in ["nobreaks", "yes"]:
		nobreaks = True
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Downloading Leaderboards... This May take a while",
			colour=discord.Colour(0x3b12ef)
			)
		)
	global_leaderboard,id_to_display_names = get_global_leaderboard(nobreaks,level_type)
	
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
				"name":f"{c+1}: {id_to_display_names[itm[0]]}",
				"value":f"Score: {itm[1]}",
				"inline":True
		}
		)
		#print(c,id_to_display_names[itm[0]], itm[1])
	await message.delete()
	pages = menus.MenuPages(source=GlobalLeaderboardViewer(lb), clear_reactions_after=True)
	await pages.start(ctx)


class GlobalLeaderboardViewer(menus.ListPageSource):
	def __init__(self, data):
		super().__init__(data, per_page=12)

	async def format_page(self, menu, entries):
		offset = menu.current_page * self.per_page
		embed = discord.Embed(
			title=f"Global Leaderboard",
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


@bot.event
async def on_command_error(ctx, error):

	send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)

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