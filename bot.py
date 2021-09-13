import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run('ODYyNzk4MTY1ODkxNzQzNzg1.YOdlaA.n1uO8QuRVhZ-8lW-SFcdwbYZyJs')