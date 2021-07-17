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
import random
from copy import deepcopy
BUCKET_URL = "https://dfp529wcvahka.cloudfront.net/manifests/leaderboards/buckets/collated.bin"
INVALID_LEVEL_TEXT = "Invalid Level."
NOT_TOP1000_TEXT = "This User is not in the top 1000 for the specified level"
NUMBER_TO_SHOW_TOP = 12
space = '\u2009'
# get important functions
from functions import *

# Initiate CacheManager.py thread

from CacheManager import *
#_thread.start_new_thread(CacheManager, ())


#print(os.path.getmtime("data/collated.json"))
#print(time.time())


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

user_log = {}
command_list = ["leaderboard", "lb", "profile", "globaltop", "weekly", "milestones", "help", "id", "link", "oldest"]

@flags.add_flag("--unbreaking",action="store_true", default=False)
@flags.add_flag("--position", type=int, default=0)
@flags.add_flag("--user", type=str)
@flags.add_flag("--price")
@flags.add_flag("--mobile",action="store_true", default=False)

@flags.command(name='leaderboard', pass_context=True,aliases=["lb"],help='Shows the leaderboard for a level')

async def leaderboard(ctx, level, **flags):

	error = {"occurred":False,"detail":""}
	#flags["position"] += -1
	if flags["position"] < 0 or flags["position"] > 1000-NUMBER_TO_SHOW_TOP:
		flags["position"] = 0
	offset = flags["position"]
	level_obj = all_levels.getByShortName(level)
	if level_obj != None: # Top command

		lb = get_top(level_obj, flags["unbreaking"])
		if flags["user"] != None and flags["price"] == None and flags["position"] == 0: # Position Command
			found_user = False
			search_for_id = re.search(r"@\w+", flags["user"])
			
			for pos,score in enumerate(lb):
				if not search_for_id:
					if score['display_name'].lower() == flags["user"].lower():
						offset = pos
						found_user = True
						break
				else:
					if score['owner']['id'] == flags["user"][1:]:
						offset = pos
						found_user = True
						break
			if not found_user:
				embed = discord.Embed(
					title=f"User Not found",
					description="The user you are looking for is not in the top 1000 for this level or you might have mistyped their username.",
					colour=discord.Colour(0xf93a2f),
				)
				await ctx.send(embed=embed)
		elif flags["price"] != None and flags["position"] == 0 and flags["user"] == None:
			price = parse_price_input(flags["price"])
			offset = 0
			prev = 0
			found_price = False
			for c,entry in enumerate(lb):
				if prev <= price and entry["value"] >= price:
					offset = c
					found_price = True
					break
				prev = entry["value"]
			if not found_price:
				embed = discord.Embed(
					title=f"Price Out of top 1000",
					description="There are no scores at that price in the top 1000.",
					colour=discord.Colour(0xf93a2f),
				)
				await ctx.send(embed=embed)
		else: # Calculate offset based on passed position and ties
			prev = 0
			for c,entry in enumerate(lb):
				if prev <= offset and entry["rank"] >= offset:
					offset = c
					break
				if entry["rank"] != prev:
					prev = entry["rank"]
		pages = menus.MenuPages(source=GeneralLeaderboardViewer(lb,f"{level}: {level_obj.name}",offset,flags["unbreaking"], level_obj.last_reloaded(), mobile_view=flags["mobile"]), clear_reactions_after=True)
		await pages.start(ctx)
	else:
		error["occurred"] = True
		error["detail"] = INVALID_LEVEL_TEXT
	if error["occurred"]:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			description=error["detail"],
			colour=discord.Colour(0xf93a2f),
		)
		await ctx.send(
			embed=embed
		)
	
bot.add_command(leaderboard)


class GeneralLeaderboardViewer(menus.ListPageSource):
	def __init__(self, data, level, offset, unbreaking, reload_time, mobile_view=False, is_weekly_challenge=False, thumbnail_url=None):
		super().__init__(data, per_page=NUMBER_TO_SHOW_TOP)
		self.level = level
		self.offs = offset
		self.unbreaking = unbreaking
		self.data = data
		self.reload_time = reload_time
		self.first = True
		self.is_weekly_challenge = is_weekly_challenge
		self.thumbnail_url = thumbnail_url
		self.mobile_view = mobile_view
		# DOES NOT APPLY OFFSET!
	async def format_page(self, menu, entries): # Entries is already a specific place
		if self.first:
			self.first = False
			menu.current_page = math.floor(self.offs/NUMBER_TO_SHOW_TOP)
			entries = self.data[(self.offs - self.offs % NUMBER_TO_SHOW_TOP):(self.offs - self.offs % NUMBER_TO_SHOW_TOP)+NUMBER_TO_SHOW_TOP]
		
		offset = (menu.current_page * self.per_page) + self.offs
		embed = discord.Embed(
			title=f"Leaderboard for {self.level} {'(Unbreaking)' if self.unbreaking else ''}",
			colour=discord.Colour(0x3586ff)
		)
		if self.is_weekly_challenge and self.thumbnail_url != None:
			embed.set_thumbnail(
				url=self.thumbnail_url
			)
		embed.set_footer(
			text=f"Page {menu.current_page+1}/{math.ceil(len(self.data)/NUMBER_TO_SHOW_TOP)} • {time_since_reload(self.reload_time)}{' • hey, this does not normally appear, I wonder what day it is?' if datetime.datetime.now().month == 4 and datetime.datetime.now().day == 1 and random.randint(0,5) == 2 else ''}"
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
		)
		description = f"`✱ = Has Breaks`\n"
		if self.mobile_view:
			for entry in entries:
				embed.add_field(
					name=f"`{'🥇🥈🥉'[entry['rank']-1] if entry['rank'] <= 3 else entry['rank']}: {entry['display_name']}`",
					value=f"{entry['price']}{' ✱' if entry['didBreak'] else ''}", # no breaking, so we don't say it broke
					inline=True,
				)
		else:
			longest = 0
			for entry in entries:
				identity = f"{'🥇🥈🥉'[entry['rank']-1] if entry['rank'] <= 3 else entry['rank']}: {entry['display_name']}"
				if (len(identity) > longest): longest = len(identity)

			for entry in entries:
				identity = f"{'🥇🥈🥉'[entry['rank']-1] if entry['rank'] <= 3 else entry['rank']}: {entry['display_name']}"
				description += f"`{identity}{' '*(longest-len(identity))} {entry['price']}{' ✱' if entry['didBreak'] else ''}`\n"
			
		embed.description = description
		#return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))
		return embed


@flags.add_flag("--unbreaking", action="store_true", default=False)
@flags.command(name='profile',help='Shows Stats about the provided user.')
async def profile(ctx, user=None, **flags):
	if user is None:
		user = ""
		if os.path.exists("data/linked.json"):
			with open("data/linked.json","rb") as f:
				data = json.load(f)
			try:
				user = data[str(ctx.message.author.id)]
			except:
				pass
		else:
			pass
	is_user_id = re.search(r"@\w+", user)
	s = time.time()
	nobreaks = flags["unbreaking"]
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Processing Data...",
			colour=discord.Colour(0x3586ff)
			)
		)
	profile_temp, owner = create_profile(user, nobreaks)
	profile = [k for k in profile_temp[:8]] + profile_temp # add 8 filler entries for the stats page
	t_profile_made = time.time()
	# find users positions on global leaderboards:
	global_positions = {}
	user_id = ""
	for level_type in ["all","regular","challenge", "weekly"]:
		global_leaderboard,id_to_display_names, worlds = get_global_leaderboard(nobreaks, level_type)
		if user != None:
				for pos,itm in enumerate(list(global_leaderboard.items())):
					if not is_user_id:
						if id_to_display_names[itm[0]].lower() == user.lower():
							user_id = itm[0]
							global_positions[level_type] = itm[1]
							break
					else:
						if itm[0] == user[1:]:
							user_id = itm[0]
							global_positions[level_type] = itm[1]
							break
	await message.delete()
	if len(list(global_positions.keys())) == 0:
		embed = discord.Embed(
			title=f"User Not found",
			description="The user you are looking for has no scores in the top 1000 for any level or you might have mistyped their username.",
			colour=discord.Colour(0xf93a2f),
		)
		await ctx.send(embed=embed)
		return
	e = time.time()
	#print("Time to get profile:", t_profile_made-s)
	#print("Time to get global scores:", e-t_profile_made)
	pages = menus.MenuPages(source=ProfileViewer(profile,flags["unbreaking"],global_positions, owner, user_id), clear_reactions_after=True)
	await pages.start(ctx)

bot.add_command(profile)

class ProfileViewer(menus.ListPageSource):
	def __init__(self, data, unbreaking, global_positions, owner, user_id, mobile_view=False):
		self.data = data[8:]
		self.unbreaking = unbreaking
		self.global_positions = global_positions
		self.owner = owner
		self.user_id = user_id
		self.mobile_view = mobile_view
		super().__init__(data, per_page=8)

	async def format_page(self, menu, entries):
		offset = menu.current_page * self.per_page
		
		if menu.current_page == 0:
			embed = discord.Embed(
				title=f"Profile for: `{self.owner}`{' (Unbreaking)' if self.unbreaking else ''}{' (Stats)' if menu.current_page == 0 else ''}, ID: `{self.user_id}`",
				description="Showing Stats page. Press :arrow_forward: in reactions to see scores for each level.",
				colour=discord.Colour(0x3586ff)
			)
			embed.set_author(
				name="PB2 Leaderboards Bot", 
				icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
			)
			global_pos_formatted = f""
			for global_score in self.global_positions.items():
				global_pos_formatted += f"{global_score[0]}: {'🥇🥈🥉'[global_score[1]['rank']] if global_score[1]['rank']+1 <= 3 else '#'+str(global_score[1]['rank']+1)} ({global_score[1]['score']})\n"
			if len(global_pos_formatted) != 0:
				embed.add_field(
						name=f"Global Leaderboard Positions",
						value=f"```{global_pos_formatted}```",
						inline=False
				)
			categories = dict.fromkeys(["overall", "regular", "challenge", "weekly"], 0)
			number_top = {
				"1":   deepcopy(categories), 
				"10":  deepcopy(categories), 
				"100": deepcopy(categories), 
				"1000":deepcopy(categories),
			}

			# all levels remain in order in self.data so we can find the level it refers to from
			# the index applied to the list all_levels.levels + weekly_levels.levels
			every_level = all_levels.levels + weekly_levels.levels
			
			for count, element in enumerate(self.data):
				level = every_level[count]
				if element["found"]:
					for rank_pool in number_top.keys():
						if element["rank"] <= int(rank_pool):
							if level.isweekly:
								number_top[rank_pool]["weekly"] += 1
								#print(f"weekly:  {level.short_name} : added to top {rank_pool}s")
							elif level.short_name.is_challenge_level:
								number_top[rank_pool]["challenge"] += 1
								#print(f"challenge:  {level.short_name} : added to top {rank_pool}s")
							else:
								number_top[rank_pool]["regular"] += 1
								#print(f"regular:  {level.short_name} : added to top {rank_pool}s")
			
			for r_id, rank_pool in number_top.items():
				number_top[r_id]["overall"] = rank_pool["regular"] + rank_pool["challenge"]
			for pool_name, values in number_top.items():
				end_val = ""
				for level_type, number in values.items():
					end_val += f"{level_type.title()}: `{number}`\n"
				
				embed.add_field(
					name=f"Top {pool_name}s",
					value=end_val,
					inline=True
				)
		else:
			embed = discord.Embed(
				title=f"Profile for: {self.owner}{' (Unbreaking)' if self.unbreaking else ''} {'(Stats)' if menu.current_page == 0 else ''}",
				colour=discord.Colour(0x3586ff),
				timestamp=datetime.datetime.now() # or any other datetime type format.
			)
			#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
			embed.set_author(
				name="PB2 Leaderboards Bot", 
				icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
			)
			embed.set_footer(text=f"Page {menu.current_page}/{math.ceil(len(self.data)/8)}")
			if self.mobile_view:
				for c, result in enumerate(entries, start=offset):
					if result["found"]:
						embed.add_field(
							name=f"{result['level']}: #{result['rank']}",
							value=f"{result['price']} {'✱' if result['didBreak'] else ''}", # no breaking, so we don't say it broke
							inline=True
						)
					elif not result["found"]:
						embed.add_field(
							name=f"{result['level']}:",
							value=f"❌",
							inline=True
						)
			else:
				description = f"`✱ = Has Breaks`\n"
				longest = 0
				for c, result in enumerate(entries, start=offset):
					if result["found"]:
						identity = f"{result['level']}: #{result['rank']}"
					else:
						identity = f"{result['level']}:"
					
					if (len(identity) > longest): longest = len(identity)

				for c, result in enumerate(entries, start=offset):
					if result["found"]:
						identity = f"{result['level']}: #{result['rank']}"
						description += f"`{identity}{' '*(longest-len(identity))} {result['price']}{' ✱' if result['didBreak'] else ''}`\n"
					else:
						identity = f"{result['level']}:"
						description += f"`{identity}{' '*(longest-len(identity))} ❌`\n"
					
					
				embed.description = description
		return embed


@flags.add_flag("--unbreaking", action="store_true", default=False)
@flags.add_flag("--mobile", action="store_true", default=False)

@flags.command(name='milestones',help='Shows Milestones for a given level')
async def milestones(ctx, level, **flags):
	nobreaks = flags["unbreaking"]
	level_obj = all_levels.getByShortName(level)
	if level_obj != None:
		milestones = get_milestones(level_obj, nobreaks)
		embed = discord.Embed(
			title=f"Milestones for {level}: {level_obj.name} {'(Unbreaking)' if nobreaks else ''}",
			colour=discord.Colour(0x3586ff),
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
		)
		embed.set_footer(
			text=f"Milestone cache last updated • {time_since_reload(refresh_bucket_collated())}",
		)
		if flags["mobile"]:
			for milestone in milestones:
				if milestone != None:
					startValue = "${:,}".format(milestone["startValue"])
					endValue = "${:,}".format(milestone["endValue"])
					embed.add_field(
						name=f"Top {milestone['percent']}%",
						value=f"#{milestone['endRank']} ({endValue})",
						inline=True
					)
		else:
			description = f""
			longest = 0
			for milestone in milestones:
				if milestone != None:
					startValue = "${:,}".format(milestone["startValue"])
					endValue = "${:,}".format(milestone["endValue"])
					identity = f"Top {milestone['percent']}%"
					if (len(identity) > longest): longest = len(identity)

			for milestone in milestones:
				if milestone != None:
					startValue = "${:,}".format(milestone["startValue"])
					endValue = "${:,}".format(milestone["endValue"])
					identity = f"Top {milestone['percent']}%"
					description += f"`{identity}{' '*(longest-len(identity))} #{milestone['endRank']} ({endValue})`\n"
			embed.description = description
		await ctx.send(
			embed=embed
		)
	else:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			description=INVALID_LEVEL_TEXT,
			colour=discord.Colour(0xf93a2f),
		)
		await ctx.send(
			embed=embed
		)

bot.add_command(milestones)
@flags.add_flag("--unbreaking", action="store_true", default=False)
@flags.add_flag("--type", type=str, default="all")
@flags.add_flag("--position", type=int, default=0)
@flags.add_flag("--user", type=str)
@flags.add_flag("--score")
@flags.add_flag("--worlds", type=str, default=None)
@flags.add_flag("--mobile", action="store_true", default=False)
@flags.add_flag("--moneyspent", action="store_true", default=False)

@flags.command(name='globaltop',help='Shows the Global Leaderboard.')

async def globaltop(ctx, **flags):
	offset = 0
	level_type = flags["type"]
	nobreaks = flags["unbreaking"]
	level_type = level_type.lower()
	if level_type not in ["all", "regular", "challenge", "weekly"] or (flags["moneyspent"] and level_type == "weekly"):
		level_type = "all"
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Processing Data...",
			colour=discord.Colour(0x3586ff)
			)
		)
	global_leaderboard, id_to_display_names, worlds = get_global_leaderboard(nobreaks, level_type, flags["moneyspent"], flags["worlds"])
	
		
	if flags["user"] != None and flags["score"] == None and flags["position"] == 0: # Position Command
		found_user = False
		search_for_id = re.search(r"@\w+", flags["user"])
		for pos,itm in enumerate(list(global_leaderboard.items())):
			if not search_for_id:
				if id_to_display_names[itm[0]].lower() == flags["user"].lower():
					offset = pos
					found_user = True
					break
			else:
				if itm[0] == flags["user"][1:]:
					offset = pos
					found_user = True
					break
		if not found_user:
			embed = discord.Embed(
				title=f"User Not found",
				description="The user you are looking for is not on the global leaderboard or you might have mistyped their username.",
				colour=discord.Colour(0xf93a2f),
			)
			await ctx.send(embed=embed)
	elif flags["score"] != None and flags["position"] == 0 and flags["user"] == None:
		price = parse_price_input(flags["score"])
		offset = 0
		prev = 0
		found_price = False
		for c,itm in enumerate(list(global_leaderboard.items())):
			entry = itm[1]
			if prev <= price and entry["score"] >= price:
				offset = c
				found_price = True
				break
			prev = entry["score"]
		if not found_price:
			embed = discord.Embed(
				title=f"Score not found",
				description="There are no at that value in the global leaderboard.",
				colour=discord.Colour(0xf93a2f),
			)
			await ctx.send(embed=embed)
	else: # Calculate offset based on passed position and ties
		offset = flags["position"]
		prev = 0
		for c,itm in enumerate(list(global_leaderboard.items())):
			entry = itm[1]
			if prev <= offset and entry["rank"] >= offset:
				offset = c
				break
			if entry["rank"] != prev:
				prev = entry["rank"]
	
	embed = discord.Embed(
			title=f"Global Leaderboard:",
			colour=discord.Colour(0x3586ff)
		)
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
	)
	lb = []
	for c,itm in enumerate(list(global_leaderboard.items())):
		lb.append({
				"name":f"{'🥇🥈🥉'[itm[1]['rank']] if itm[1]['rank']+1 <= 3 else itm[1]['rank']+1}: {id_to_display_names[itm[0]]}",
				"value":f"Spent: {'${:,}'.format(int(itm[1]['score']))}" if flags["moneyspent"] else f"Score: {itm[1]['score']}",
				"inline":True
		}
		)
		#print(c,id_to_display_names[itm[0]], itm[1])
	await message.delete()
	pages = menus.MenuPages(source=GlobalLeaderboardViewer(lb, offset, level_type, nobreaks, worlds, mobile_view=flags["mobile"]), clear_reactions_after=True)
	await pages.start(ctx)


bot.add_command(globaltop)
class GlobalLeaderboardViewer(menus.ListPageSource):
	def __init__(self, data, offset, level_type, unbreaking, worlds, mobile_view=False):
		self.data = data
		self.offs = offset
		self.first = True
		self.level_type = level_type
		self.unbreaking = unbreaking
		self.worlds = worlds
		self.mobile_view = mobile_view
		super().__init__(data, per_page=12)

	async def format_page(self, menu, entries):
		if self.first:
			self.first = False
			menu.current_page = math.floor(self.offs/NUMBER_TO_SHOW_TOP)
			entries = self.data[(self.offs - self.offs % NUMBER_TO_SHOW_TOP):(self.offs - self.offs % NUMBER_TO_SHOW_TOP)+NUMBER_TO_SHOW_TOP]
		offset = (menu.current_page * self.per_page) + self.offs
		
		title = "Global Leaderboard"
		if self.worlds:
			title += ' (World{s} `{worlds}`)'.format(worlds=",".join(self.worlds), s="s" if len(self.worlds) > 1 else "")
		else:
			title += f" ({self.level_type} levels)"
		if self.unbreaking:
			title += ' (Unbreaking)'
		
		embed = discord.Embed(
			title=title,
			colour=discord.Colour(0x3586ff)
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
		)
		embed.set_footer(text=f"Page {menu.current_page+1}/{math.ceil(len(self.data)/NUMBER_TO_SHOW_TOP)}")
		if self.mobile_view:
			for c, result in enumerate(entries, start=offset):
				embed.add_field(
					name=f"`{result['name']}`",
					value=result["value"],
					inline=result["inline"]
				)
		else:
			longest = 0
			description = f""
			for c, result in enumerate(entries, start=offset):
				identity = f"{result['name']}"
				if (len(identity) > longest): longest = len(identity)

			for c, result in enumerate(entries, start=offset):
				identity = f"{result['name']}"
				description += f"`{identity}{' '*(longest-len(identity))} {result['value']}`\n"
			embed.description = description
		
		#return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))
		return embed


@flags.add_flag("--week", type=int, default=0)
@flags.add_flag("--unbreaking", action="store_true", default=False)
@flags.add_flag("--position", type=int, default=0)
@flags.add_flag("--user", type=str)
@flags.add_flag("--price")
@flags.add_flag("--mobile",action="store_true", default=False)
@flags.command(name='weekly',help='Show Weekly Challenge Leaderboards.')
#@commands.cooldown(1, 5, commands.BucketType.user)

async def weeklyChallenge(ctx, **flags):
	challenge_weeks = {}
	week = flags["week"]
	if week < 1 or week > len(weekly_levels.levels):
		week = weekly_levels.levels[-1].week
	error = {"occurred":False,"detail":""}
	#flags["position"] += -1
	if flags["position"] < 0 or flags["position"] > 1000-NUMBER_TO_SHOW_TOP:
		flags["position"] = 0
	offset = flags["position"]
	level_obj = weekly_levels.getByWeek(week)
	
	if level_obj != None: # Top command

		lb = get_top(level_obj, flags["unbreaking"])
		if flags["user"] != None and flags["price"] == None and flags["position"] == 0: # Position Command
			found_user = False
			search_for_id = re.search(r"@\w+", flags["user"])
			for pos,score in enumerate(lb):
				if not search_for_id:
					if score['display_name'].lower() == flags["user"].lower():
						offset = pos
						found_user = True
						break
				else:
					if score['owner']['id'] == flags["user"][1:]:
						offset = pos
						found_user = True
						break
			if not found_user:
				embed = discord.Embed(
					title=f"User Not found",
					description="The user you are looking for is not in the top 1000 for this level or you might have mistyped their username.",
					colour=discord.Colour(0xf93a2f),
				)
				await ctx.send(embed=embed)
		elif flags["price"] != None and flags["position"] == 0 and flags["user"] == None:
			price = parse_price_input(flags["price"])
			offset = 0
			prev = 0
			found_price = False
			for c,entry in enumerate(lb):
				if prev <= price and entry["value"] >= price:
					offset = c
					found_price = True
					break
				prev = entry["value"]
			if not found_price:
				embed = discord.Embed(
					title=f"Price Out of top 1000",
					description="There are no scores at that price in the top 1000.",
					colour=discord.Colour(0xf93a2f),
				)
				await ctx.send(embed=embed)
		else: # Calculate offset based on passed position and ties
			prev = 0
			for c,entry in enumerate(lb):
				if prev <= offset and entry["rank"] >= offset:
					offset = c
					break
				if entry["rank"] != prev:
					prev = entry["rank"]
		pages = menus.MenuPages(source=GeneralLeaderboardViewer(lb,level_obj.name,offset,flags["unbreaking"], level_obj.last_reloaded(), mobile_view=flags["mobile"], is_weekly_challenge=True, thumbnail_url=level_obj.preview), clear_reactions_after=True)
		await pages.start(ctx)
	else:
		error["occurred"] = True
		error["detail"] = INVALID_LEVEL_TEXT
	if error["occurred"]:
		embed = discord.Embed(
			title=f"An Error Occurred.",
			description=error["detail"],
			colour=discord.Colour(0xf93a2f),
		)
		await ctx.send(
			embed=embed
		)
	

bot.add_command(weeklyChallenge)


@flags.add_flag("--unbreaking", action="store_true", default=False)
#@flags.add_flag("--user", type=str)
@flags.add_flag("--level", type=ShortName)
@flags.add_flag("--uploadhistory", action="store_true", default=False)
@flags.add_flag("--mobile", action="store_true", default=False)

@flags.command(name='oldest',help='Shows the positions which have been held for the longest.')

async def oldest_scores(ctx, **flags):
	level = flags.get("level")
	offset = 0
	message = await ctx.send(
		embed = discord.Embed(
			title=f"Processing Data...",
			colour=discord.Colour(0x3586ff)
		)
	)
	scores = get_oldest_scores_leaderboard(unbroken=flags["unbreaking"])
	if level:
		scores = compute_oldest_ranks([score for score in scores if score["level_short_name"] == str(level)])
		l = all_levels.getByShortName(str(level))
		if l and flags["uploadhistory"]:
			data = {
				"any": l.leaderboard["any"]["top_history"],
				"unbroken": l.leaderboard["unbroken"]["top_history"],
			}
			with open("data/temp.temp", "w") as f:
				json.dump(data, f)
			with open("data/temp.temp", "rb") as f:
				await ctx.send(
					file = discord.File(f, filename=f"oldest_data_{level}.json")
				)
	now = time.time()
	await message.delete()
	pages = menus.MenuPages(source=OldestLeaderboardViewer(scores, offset, flags["unbreaking"], flags["mobile"]), clear_reactions_after=True)
	await pages.start(ctx)

bot.add_command(oldest_scores)

class OldestLeaderboardViewer(menus.ListPageSource):
	def __init__(self, data, offset, unbroken=False, mobile_view=False):
		self.data = data
		self.offs = offset
		self.first = True
		self.unbroken = unbroken
		self.mobile_view = mobile_view
		super().__init__(data, per_page=12)

	async def format_page(self, menu, entries):
		now = time.time()
		if self.first:
			self.first = False
			menu.current_page = math.floor(self.offs/NUMBER_TO_SHOW_TOP)
			entries = self.data[(self.offs - self.offs % NUMBER_TO_SHOW_TOP):(self.offs - self.offs % NUMBER_TO_SHOW_TOP)+NUMBER_TO_SHOW_TOP]
		offset = (menu.current_page * self.per_page) + self.offs
		
		title = "Oldest Scores" + " (Unbreaking)" if self.unbroken else ""
		
		embed = discord.Embed(
			title=title,
			colour=discord.Colour(0x3586ff),
		)
		#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
		embed.set_author(
			name="PB2 Leaderboards Bot", 
			icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
		)
		embed.set_footer(text=f"Page {menu.current_page+1}/{math.ceil(len(self.data)/NUMBER_TO_SHOW_TOP)}")
		if self.mobile_view:
			for c, result in enumerate(entries, start=offset):
				embed.add_field(
					name=f"`{result['time_rank']}: {result['level_short_name']} - {str(result.get('num_players', 0))+' people' if result.get('num_players', 0) else result['owner']['display_name']}`",
					value=f"{nice_time_format(now-result['time'])}",
					inline=True
				)
				#print(f"{c+1}: {i['level_short_name']} - #{i['rank']} - {nice_time_format(now-i['time'])}")
		else:
			pass
			longest = 0
			description = f"`✱ = Has Breaks`\n"
			for c, result in enumerate(entries, start=offset):
				identity = f"{'🥇🥈🥉'[result['time_rank']-1] if result['time_rank'] <= 3 else result['time_rank']}: {result['level_short_name']} - {str(result.get('num_players', 0))+' people' if result.get('num_players', 0) else result['owner']['display_name']}"
				if (len(identity) > longest): longest = len(identity)

			for c, result in enumerate(entries, start=offset):
				identity = f"{'🥇🥈🥉'[result['time_rank']-1] if result['time_rank'] <= 3 else result['time_rank']}: {result['level_short_name']} - {str(result.get('num_players', 0))+' people' if result.get('num_players', 0) else result['owner']['display_name']}"
				description += f"`{identity}{' '*(longest-len(identity))} {nice_time_format(now-result['time'])}{' ✱' if result['didBreak'] else ''}`\n"
			embed.description = description
		#return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))
		return embed


@bot.command(name='id',help='Get the ID of a user')
async def get_user_id(ctx,user):
	users = id_from_user(user)
	embed = discord.Embed(
		title=f"Users with the name: {user}",
		colour=discord.Colour(0x3586ff)
	)
	#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
	)
	for user in users:
		embed.add_field(
			name=user["id"],
			value=user["display_name"],
			inline=True
		)
	if len(users) == 0:
		embed.add_field(
			name="Error",
			value="No Users found with that name",
			inline=False
		)
	await ctx.send(embed=embed)


#bot.add_command(get_user_id)

@bot.command(name='link',help='Link your discord account to a member on the leaderboards')
async def link(ctx,user=None):
	
	try:
		with open("data/linked.json","rb") as f:
			data = json.load(f)
	except:
		data = {}
	if user:
		with open("data/linked.json","w") as f:
			data[str(ctx.message.author.id)] = user
			json.dump(data, f)
	embed = discord.Embed(
		title=f"Linked your Discord account to the user: {user}" if user else f"Your Discord account is linked to the user: {data.get(str(ctx.message.author.id), '**Account not linked!**')}",
		colour=discord.Colour(0x3586ff)
	)
	#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png"
	)
	await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):

	send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError, flags._parser.ArgumentParsingError)
	if isinstance(error, commands.CommandNotFound):  # fails silently
		#await ctx.send("```Invalid Command.```")
		pass

	elif isinstance(error, send_help):
		await ctx.invoke(bot.get_command('help'), command_name=str(ctx.command))

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

bot.remove_command("help")
@bot.command(name='help',help='Shows this message!')

async def help(ctx, command_name=None):
	if command_name:
		# assuming there is a command_name parameter
		for command in bot.commands:
			if command_name == command.name or command_name in command.aliases:
				try:
					with open(f"docs/{command.name}/title.txt", "r") as title:
						with open(f"docs/{command.name}/description.txt", "r") as desc:
							title_data = title.read()
							desc_data = desc.read()
							if title_data and desc_data:
								embed = discord.Embed(title=title_data,description=desc_data)
							else:
								raise FileNotFoundError
					await ctx.send(embed=embed)
				except FileNotFoundError:
					await ctx.send("Sorry, the command requested has no documentation associated with it and/or the command does not exist.")
					pass
	else:
		embed = discord.Embed(title="Commands")
		for command in bot.commands:
			embed.add_field(name=f"-{command.name}",value=f"{command.help}\nDocumentation: `-help {command.name}`")
		await ctx.send(embed=embed)
		# Show overviews
@bot.event
async def on_message(message):
	if isinstance(message.channel, discord.DMChannel):
			return
	if message.author.bot:
			return

	await bot.process_commands(message)


@bot.event
async def on_ready():
	print("[Bot] Connected to Discord!")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="-help"))

if __name__ == "__main__":
	_thread.start_new_thread(CacheManager, ())

bot.run(TOKEN)
loop = asyncio.get_event_loop()

