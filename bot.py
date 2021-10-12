import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import youtube_dl
import asyncio

client = commands.Bot(command_prefix='!')

queues = {}
now_playing = {}
ydl_opts = {
    'format': 'bestaudio/best', 'ignoreerrors': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

ytdl = youtube_dl.YoutubeDL(ydl_opts)
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


async def start_message(ctx, title):
    embed = discord.Embed(title="",
                          description=f":notes: Playing \n `{title}` \n - Now!\n {ctx.author.mention}",
                          color=discord.Color(0xff3aab))
    await ctx.send(embed=embed)


def start(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if len(queues[ctx.guild.id]) > 0:
        if voice is None or not voice.is_playing():
            title = queues[ctx.guild.id][0][0]
            source = queues[ctx.guild.id][0][1]
            print(source)
            voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: start(ctx))
            voice.is_playing()
            asyncio.run_coroutine_threadsafe(start_message(ctx, title), ctx.bot.loop)
            print("voiice", voice.is_playing())
            now_playing[ctx.guild.id] = queues[ctx.guild.id][0][0]

            print("now", now_playing[ctx.guild.id])
            queues[ctx.guild.id].pop(0)
        else:
            voice = None


async def add(ctx, title, source):
    if len(queues[ctx.guild.id]) == 0:
        queues[ctx.guild.id].insert(0, [title, source])
    else:
        queues[ctx.guild.id].append([title, source])
    print(queues)
    print(len(queues[ctx.guild.id]))
    embed = discord.Embed(title="",
                          description=f":pencil: Added song: \n `{title}` \n - To queue! \n {ctx.author.mention}",
                          color=discord.Color(0xff3aab))
    await ctx.send(embed=embed)


async def search_message(ctx, url):
    embed = discord.Embed(title="",
                          description=f":mag_right: Searching for: \n `{url}` \n {ctx.author.mention}",
                          color=discord.Color(0xff3aab))
    await ctx.send(embed=embed)


def search(query):
    with ytdl:
        try:
            requests.get(query)
        except:
            info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

        else:
            info = ytdl.extract_info(query, download=False)
        return info['title'], info, info['formats'][0]['url']


@client.event
async def on_ready():
    print("attackontitan {0.user}".format(client))


@client.command()
async def play(ctx, *, url):
    voice_channel = ctx.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice is None or not voice.is_connected:
        await voice_channel.connect()
    else:
        pass
    print("voice", voice)
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    print("queuq", queues)
    print(url)
    await search_message(ctx, url)
    title, video, source = search(url)
    await add(ctx, title, source)
    start(ctx)


@client.command()
async def queue(ctx):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    retval = ""
    for i in range(0, len(queues[ctx.guild.id])):
        retval += "`" + queues[ctx.guild.id][i][0] + "`" + "\n"
    print(retval)
    if retval != "":
        embed = discord.Embed(title="",
                              description=f":notes:Queue is: \n {retval}\n[{ctx.author.mention}]",
                              color=discord.Color(0xff3aab))
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="",
                              description=f"Queue is empty! \n [{ctx.author.mention}]",
                              color=discord.Color(0xff3aab))
        await ctx.send(embed=embed)


@client.command()
async def now(ctx):
    if ctx.guild.id in now_playing:
        embed = discord.Embed(title="",
                              description=f"Currently playing: \n `{now_playing[ctx.guild.id]}` \n{ctx.author.mention}",
                              color=discord.Color(0xff3aab))
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="",
                              description=f"Nothing is playing right now! \n{ctx.author.mention}",
                              color=discord.Color(0xff3aab))
        await ctx.send(embed=embed)


@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            voice.stop()
            await start(ctx)
    except:
        AttributeError


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_connected():
            await voice.disconnect()
    except:
        AttributeError


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            voice.pause()
        else:
            embed = discord.Embed(title="",
                                  description=f"No audio is playing! \n [{ctx.author.mention}]",
                                  color=discord.Color(0xff3aab))
            await ctx.send(embed=embed)
    except:
        AttributeError

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_paused():
            voice.resume()
        else:
            embed = discord.Embed(title="",
                                  description=f"Audio is not paused! \n [{ctx.author.mention}]",
                                  color=discord.Color(0xff3aab))
            await ctx.send(embed=embed)
    except:
        AttributeError



@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            queues[ctx.guild.id].clear()
            voice.stop()
    except:
        AttributeError



with open("token.txt") as file:
    token = file.read()
client.run(token)
