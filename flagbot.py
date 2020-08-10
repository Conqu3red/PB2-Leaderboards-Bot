import discord
from discord.ext import flags, commands

# CODE NOT MEANT TO BE EXECUTED !

bot = commands.Bot("!")

# Invocation: !flags --count=5 --string "hello world" --user Xua --thing y

@flags.add_flag("--count", type=int, default=10)
@flags.add_flag("--string", default="hello!")
@flags.add_flag("--user", type=discord.User)
@flags.add_flag("--thing", type=bool)
@flags.command()
async def flag(ctx, **flags):
    await ctx.send("--count={count!r}, --string={string!r}, --user={user!r}, --thing={thing!r}".format(**flags))


@flags.add_flag("--str", default="hello!")
@flags.command(name="b")
async def a(ctx, **flags):s
	await ctx.send("--str={str!r}".format(**flags))
bot.run("NzM1Mzk5NDAwNzI1MTUxNzY2.Xxftew.P-hFJ98fX6Y_n3zPabVjyYjsTPs")
