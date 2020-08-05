import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os
import datetime
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')
@bot.command(name="e",help="e")

async def e(ctx):
	embed = discord.Embed(
		title="Top 10",
		colour=discord.Colour(0x3b12ef),
		description="this supports [named links](https://discord.com/) on top of the subset of markdown.\nYou can use newlines too!",
		timestamp=datetime.datetime.now() # or any other datetime type format.
	)
	#embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
	embed.set_author(
		name="PB2 Leaderboards Bot", 
		icon_url="https://lh6.googleusercontent.com/72OW4e9jKhufyDZ3aUPD0adWhsEav2xc8Yb79a9TomiyxrQkOCci-KwHDCMFNvY8WrziQ29QUDA_7Tl9gHuA=w1920-h915"
	)
	embed.set_footer(
		text="Cache Last Updated",
	)
	
	embed.add_field(
		name="Rank",
		value=""
	)
	embed.add_field(
		name="Breaks?",
		value=""
	)
	embed.add_field(
		name="Name",
		value=""
	)
	embed.add_field(
		name="Price",
		value=""
	)
	await ctx.send(
		content="This is a normal message to be sent alongside the embed",
		embed=embed
	)

bot.run(TOKEN)