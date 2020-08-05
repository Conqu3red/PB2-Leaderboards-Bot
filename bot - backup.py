import requests
from datetime import *
import time
import os
import asyncio
import json
import re
import discord
from tabulate import tabulate
from discord.ext import commands
from dotenv import load_dotenv
INVALID_LEVEL_TEXT = "Error: Invalid Level."
NOT_TOP1000_TEXT = "This User is not in the top 1000 for the specified level"
#print(os.path.getmtime("data/collated.json"))
#print(time.time())
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"
identifiers = {
"1": ["mAp2V", "NAgrb", "Bbm2A", "0A5Zn", "JbOmn", "aVeaV", "5VlRA", "gnR7V", "7b7xA", "WAGoA", "ObqMb", "EAaRn", "Xb3Ob", "1nXeV", "EABGn", "6Vw5A"],    #World 1
"2": ["zA0Mn", "kb2wA", "gb1Kn", "ZAoeV", "MAr3n", "QVYRb", "JnZ2n", "PV4Qb", "yb8Pb", "gnyrV", "MAEoV", "qn9JV", "5AWzb", "MV6DA", "1nQen", "bmw2n"],    #World 2
"3": ["jnL9V", "vAMDb", "lnKkn", "bdjrn", "JbDPb", "mnkRA", "Ap22V", "abx5A", "5VJBV", "zAvPV", "JVPon", "ZbjWA", "XVzGb", "A5QZA", "ObNoA", "AgXrn"],    #World 3
"4": ["nk2rA", "nKv3A", "bje7V", "b2qZV", "VPllV", "nyl7A", "VY39A", "Av89V", "bxeQA", "AW4kn", "bDDrb", "nQlOA", "nZLOb", "n9ZBV", "AM8vb", "V6BNV"],    #World 4
"5": ['nRM67', 'b7l7x', 'AGDKo', 'bqYEM', 'Aa58R', 'b3WOO', 'nXZMe', 'AB1QG', 'VwMk5', 'A0ZgM', 'AoqEe', 'b1WmK', 'AEOYo', 'VY3MR', 'nKvxk', 'nZLM2'],    #World 5 :)
"1c": ["AW7zA", "bq7Mn", "Aa7RV", "Ao2eb", "nXLen", "Vw85b", "V6qDn", "nK8kV", "b33Ob", "A0rMV", "nZ32V", "VY4Rn", "ABDGV", "AEBon", "b1qKb", "n9dJA"],   #World 1c
"2c": ["VzoGb", "nQOeb", "b2WwA", "nyXrA", "AMmDA", "VJDBA", "AvMPb", "bN5oV", "bDzPn", "bxN5n", "nklRV", "VPgon", "b83PV", "bjMWV", "nLm9V", "V4LQV"],   #World 2c
"3c": ["Vezab", "Arl3V", "bdarA", "A5GZV", "bqYMb", "AGDon", "ApQ9n", "ApQ2n", "AgrJb", "bdaqA", "Agrrb", "b7lxA", "bmK2n", "Vl5Rb", "bOpmA", "nRM7A"],   #World 3c
"4c": ["b7ljA", "bOpaA", "Aa5OA", "VwMpA", "A0ZaV", "bqYob", "A5GJV", "b3WDb", "nXZzb", "nRM8A", "AGD6n", "AB19b", "Vez1b", "bmK9n", "AoqpV", "Vl5gb"],   #World 4c
"5c": ['V6BRD', 'Av8NP', 'bx3E5', 'nQm4e', 'b2Z5w', 'VPeKo', 'VJGKB', 'bNdLo', 'V45eQ', 'b8zGP', 'VzJ2G', 'nLar9', 'ArdM3', 'bdaJr', 'ApQj2', 'AgrJr'],   #World 5c :)
"51": ['bm2OL', 'A5XOx', 'bOeMR', 'VeDY5', 'Vl2Wp', 'nR5Re', 'b7WRR', 'AGvLD', 'bqe7e', 'AaE79', 'b3Y34', 'nXvLa', 'ABND7', 'Vwa8y', 'A0QrO', 'Aor26']    #Secret World :)
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
	if current_time - cache_last_reloaded > 28800 or override: # 8 hours
		url = download_url.format(leaderboard_id)
		r = requests.get(url)
		with open(f"data/{leaderboard_id}.json", "wb") as cache_file:
			cache_file.write(r.content)



def top10(leaderboard_id, unbroken=False):
	refresh_data(leaderboard_id)
	referer = "any"
	if unbroken:
		referer = "unbroken"
	with open(f"data/{leaderboard_id}.json", "r") as file:
		file = json.load(file)
		leaderboard_data = file[referer]["top1000"]
		formatted = []
		for rank,score in enumerate(leaderboard_data[:10]):
			#print(score)
			formatted.append([rank+1,"yes" if score["didBreak"] else "no",score["owner"]["display_name"],"${:,}".format(score["value"])])
			if len(formatted) > 1:
				if score["value"] == formatted[rank-1][3]: # Allign ranks for scores that tie
					formatted[len(formatted)-1][0] = formatted[rank-1][0]
		table = tabulate(formatted, headers=["Rank","Breaks?","Name", "Price"],tablefmt="pipe", colalign=("right","left","left","right"))
		print(table)
		return table

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
				formatted.append([rank+1,"yes" if score["didBreak"] else "no",score["owner"]["display_name"],score["value"]])
		if len(formatted) > 0:
			table = tabulate(formatted, headers=["Rank","Breaks?","Name", "Price"],tablefmt="pipe")
			print(table)
		else:
			table = NOT_TOP1000_TEXT
		return table








def create_profile(user, unbroken):
	referer = "any"
	if unbroken:
		referer = "unbroken"
	global levels
	#for level in levels:
	#	get_level_id(level)
	generated = []
	for level in levels:
		leaderboard_id = get_level_id(level)
		with open(f"data/{leaderboard_id}.json", "r") as file:
			file = json.load(file)
			leaderboard_data = file[referer]["top1000"]
			found = False
			for rank,score in enumerate(leaderboard_data):
				if score["owner"]["display_name"] == user:
					found = True
					this_level = [level,rank+1,score['value'],"yes" if score["didBreak"] else "no"]
			if not found:
				this_level = [level]
			generated.append(this_level)
			#print(this_level)
	nice = tabulate(generated, headers=["Level","Rank","Price","Breaks?"],tablefmt="pipe")
	joined = f"Generated Profile for {user}\n{nice}"
	with open("temp","w") as temp:
		temp.write(joined)
	#print(joined)
	return "```Please see attached file for profile data```"


levels = []
for c in range(2):
	for world in range(4):
		for level in range(16):
			levels.append(f"{world+1}-{level+1}{'c' if c == 1 else ''}")
#print(levels)






def remove_non_ascii(text):
	return ''.join([i if ord(i) < 128 else '?' for i in text])


#string = input("Enter a level: ")
#level_id = get_level_id(string)
#top10(level_id, True)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

@bot.command(name='top',help='Get top leaderboard for a level\nAppend nobreaks to remove results with breaks')

async def top(ctx, level, unbreaking="no"):
	nobreaks = False
	if unbreaking.lower() == "nobreaks":
		nobreaks = True
	level_id = get_level_id(level)
	if level_id != INVALID_LEVEL_TEXT:
		lb = top10(level_id, nobreaks)
		lb = remove_non_ascii(lb)
		await ctx.send(f"```Top 10 for {level}\n{lb}```")
	else:
		await ctx.send(f"```{INVALID_LEVEL_TEXT}```")


@bot.command(name='position',help='Get the position of a specific user on a certain level')

async def position(ctx, level, user, unbreaking="no"):
	nobreaks = False
	if unbreaking.lower() == "nobreaks":
		nobreaks = True
	level_id = get_level_id(level)
	if level_id != INVALID_LEVEL_TEXT:
		lb = find_user(level_id, user, nobreaks)
		lb = remove_non_ascii(lb)
		if lb != NOT_TOP1000_TEXT:
			await ctx.send(f"```Score for {user} on {level}\n{lb}```")
		else: 
			await ctx.send(f"```{lb}```")
	else:
		await ctx.send(f"```{INVALID_LEVEL_TEXT}```")

@bot.command(name='profile',help='Get Profile of a user - may take a while!')
async def profile(ctx, user, unbreaking="no"):
	nobreaks = False
	if unbreaking.lower() == "nobreaks":
		nobreaks = True
	profile = create_profile(user, nobreaks)
	area=ctx.message.channel
	await ctx.send(file=discord.File("temp",filename=f"Profile of {user}.txt",),content=profile)


bot.run(TOKEN)