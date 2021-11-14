import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import youtube_dl
import asyncio
import time
from discord.ext import tasks
import json


def get_prefix(client, ctx):  # first we define get_prefix
    with open('prefixes.json', 'r') as f:  # we open and read the prefixes.json, assuming it's in the same file
        prefixes = json.load(f)  # load the json as prefixes
    return prefixes[str(ctx.guild.id)]  # recieve the prefix for the guild id given


client = commands.Bot(command_prefix=get_prefix, help_command=None)

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


async def start_playing_message(ctx, title, duration, channel, channel_url, webpage_url, thumbnail, author):
    embed = discord.Embed(description=f"[{title}]({webpage_url})", color=discord.Color(0xe974b5))
    embed.set_author(name="Playing:", icon_url=f"{author.avatar_url}")
    embed.set_thumbnail(url=f"{thumbnail}")
    embed.add_field(name="Channel", value=f"[{channel}]({channel_url})", inline=True)
    embed.add_field(name="Duration", value=f"{duration}", inline=True)
    await ctx.send(embed=embed)


def play_music(ctx):
    try:
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if len(queues[ctx.guild.id]) > 0:
            if voice is None or not voice.is_playing():
                title = queues[ctx.guild.id][0]['title']
                source = queues[ctx.guild.id][0]['source']
                duration = queues[ctx.guild.id][0]['duration']
                channel = queues[ctx.guild.id][0]['channel']
                channel_url = queues[ctx.guild.id][0]['channel_url']
                webpage_url = queues[ctx.guild.id][0]['webpage_url']
                thumbnail = queues[ctx.guild.id][0]['thumbnail']
                author = queues[ctx.guild.id][0]['author']
                voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: play_music(ctx))
                voice.is_playing()
                asyncio.run_coroutine_threadsafe(start_playing_message(ctx, title, duration, channel, channel_url,
                                                                       webpage_url, thumbnail, author), ctx.bot.loop)
                now_playing[ctx.guild.id] = queues[ctx.guild.id][0]
                queues[ctx.guild.id].pop(0)
    except:
        AttributeError


async def add(ctx, title, source, duration, channel, channel_url, webpage_url, thumbnail, author):
    if ctx.guild.id not in now_playing:
        now_playing[ctx.guild.id] = {}
    if len(queues[ctx.guild.id]) == 0 and len(now_playing[ctx.guild.id]) == 0:
        queues[ctx.guild.id].insert(0, {'title': title, 'source': source, 'duration': duration, 'channel': channel,
                                        'channel_url': channel_url, 'webpage_url': webpage_url, 'thumbnail': thumbnail,
                                        'author': author})
    elif len(queues[ctx.guild.id]) == 0 and len(now_playing[ctx.guild.id]) != 0:
        queues[ctx.guild.id].append({'title': title, 'source': source, 'duration': duration, 'channel': channel,
                                     'channel_url': channel_url, 'webpage_url': webpage_url, 'thumbnail': thumbnail,
                                     'author': author})
        embed = discord.Embed(description=f"[{title}]({webpage_url})", color=discord.Color(0xe974b5))
        embed.set_author(name="Added to queue:", icon_url=f"{author.avatar_url}")
        embed.set_thumbnail(url=f"{thumbnail}")
        embed.add_field(name="Channel", value=f"[{channel}]({channel_url})", inline=True)
        embed.add_field(name="Duration", value=f"{duration}", inline=True)
        await ctx.send(embed=embed)
    else:
        queues[ctx.guild.id].append({'title': title, 'source': source, 'duration': duration, 'channel': channel,
                                     'channel_url': channel_url, 'webpage_url': webpage_url, 'thumbnail': thumbnail,
                                     'author': author})
        embed = discord.Embed(description=f"[{title}]({webpage_url})", color=discord.Color(0xe974b5))
        embed.set_author(name="Added to queue:", icon_url=f"{author.avatar_url}")
        embed.set_thumbnail(url=f"{thumbnail}")
        embed.add_field(name="Channel", value=f"[{channel}]({channel_url})", inline=True)
        embed.add_field(name="Duration", value=f"{duration}", inline=True)
        await ctx.send(embed=embed)


async def search_message(ctx, url):
    embed = discord.Embed(description=f"{url}", colour=discord.Color(0xe974b5))
    embed.set_author(name="Searching for:", icon_url=f"{ctx.author.avatar_url}")
    await ctx.send(embed=embed)


def search(query):
    with ytdl:
        try:
            requests.get(query)
        except:
            info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

        else:
            info = ytdl.extract_info(query, download=False)
        return info['title'], info['formats'][0]['url'], info['duration'], info['channel'], info['channel_url'], \
               info['webpage_url'], info['thumbnail']


@client.event
async def on_ready():
    print("attackontitan {0.user}".format(client))


@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '!'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.command()
async def play(ctx, *, url):
    try:
        voice_channel = ctx.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice is None or not voice.is_connected:
            await voice_channel.connect()
        else:
            pass
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []
        await search_message(ctx, url)
        title, source, duration, channel, channel_url, webpage_url, thumbnail = search(url)
        author = ctx.author

        def seconds_to_minutes(duration):
            minutes = str(duration // 60)
            seconds = duration % 60
            if seconds < 10:
                seconds = "0" + str(seconds)

            duration = minutes + ":" + str(seconds)
            return duration

        duration = (seconds_to_minutes(duration))
        await add(ctx, title, source, duration, channel, channel_url, webpage_url, thumbnail, author)
        play_music(ctx)

        @tasks.loop(minutes=5)
        async def count():
            if len(voice_channel.members) == 1:
                await leave(ctx)
                count.stop()

        count.start()
    except:
        AttributeError


@client.command()
async def queue(ctx):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    if len(queues[ctx.guild.id]) != 0:
        embed = discord.Embed(color=discord.Color(0xe974b5))
        embed.set_author(name=f"Queue", icon_url=f"{ctx.author.avatar_url}")
        for i in range(0, len(queues[ctx.guild.id])):
            embed.add_field(name="\u200b", value=f"**{i + 1}.** [{queues[ctx.guild.id][i]['title']}]"
                                                 f"({queues[ctx.guild.id][i]['webpage_url']})", inline=False)
            i += 1
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=discord.Color(0xe974b5))
        embed.set_author(name=f"Queue is empty!", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=embed)


@client.command()
async def clear(ctx):
    if ctx.guild.id in queues:
        if not len(queues[ctx.guild.id]) == 0:
            queues[ctx.guild.id].clear()
            embed = discord.Embed(color=discord.Color(0xe974b5))
            embed.set_author(name="Queue cleared!", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=discord.Color(0xe974b5))
            embed.set_author(name="Queue is already empty!", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=embed)


@client.command()
async def now(ctx):
    if ctx.guild.id in now_playing:
        title = now_playing[ctx.guild.id]['title']
        duration = now_playing[ctx.guild.id]['duration']
        channel = now_playing[ctx.guild.id]['channel']
        channel_url = now_playing[ctx.guild.id]['channel_url']
        webpage_url = now_playing[ctx.guild.id]['webpage_url']
        thumbnail = now_playing[ctx.guild.id]['thumbnail']
        author = now_playing[ctx.guild.id]['author']
        embed = discord.Embed(title="", description=f"[{title}]({webpage_url})", color=discord.Color(0xe974b5))
        embed.set_author(name="Currently playing:", icon_url=f"{author.avatar_url}")
        embed.set_thumbnail(url=f"{thumbnail}")
        embed.add_field(name="Channel", value=f"[{channel}]({channel_url})", inline=True)
        embed.add_field(name="Duration", value=f"{duration}", inline=True)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=discord.Color(0xe974b5))
        embed.set_author(name="Nothing is playing right now!", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=embed)


@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            voice.stop()
            if ctx.guild.id in now_playing:
                now_playing.pop(ctx.guild.id)
            await play_music(ctx)
    except:
        AttributeError


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_connected():

            if ctx.guild.id in queues:
                queues.pop(ctx.guild.id)
            if ctx.guild.id in now_playing:
                now_playing.pop(ctx.guild.id)

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
            embed = discord.Embed(color=discord.Color(0xe974b5))
            embed.set_author(name="No audio is playing!", icon_url=f"{ctx.author.avatar_url}")
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
            embed = discord.Embed(color=discord.Color(0xe974b5))
            embed.set_author(name="Audio is not paused!", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=embed)
    except:
        AttributeError


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            queues.pop(ctx.guild.id)
            now_playing.pop(ctx.guild.id)
            voice.stop()
    except:
        AttributeError


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def prefix(ctx, pref):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = pref

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    embed = discord.Embed(description=f"{pref}", colour=discord.Color(0xe974b5))
    embed.set_author(name="Prefix changed to:", icon_url=f"{ctx.author.avatar_url}")
    await ctx.send(embed=embed)


@client.command()
async def help(ctx):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
        pref = prefixes[str(ctx.guild.id)]
        bonbon = await client.fetch_user(327132988326543371)  # 0xff3aab cтарый цвет
    embed = discord.Embed(title=f"Список команд", description=f"Префикс - **{pref}**", color=discord.Color(0xe974b5))
    embed.set_author(name="Автор: bonbon", url="https://github.com/bonbon195", icon_url=bonbon.avatar_url)
    embed.add_field(name="help", value="Показать это сообщение")
    embed.add_field(name="pause", value="Поставить песню на паузу")
    embed.add_field(name="resume", value="Продолжить")
    embed.add_field(name="stop", value="Остановить проигрывание песни и очистить очередь")
    embed.add_field(name="leave", value="Выйти из голосового канала")
    embed.add_field(name="queue", value="Показать очередь")
    embed.add_field(name="clear", value="Очистить очередь")
    embed.add_field(name="now", value="Показать какая песня сейчас играет")
    embed.add_field(name="skip", value="Перейти к следующей песне в очереди")
    embed.add_field(name="play", value=f"Играть музыку. Бот принимает значения в формате:\n"
                                       f"{pref}play название песни\n"
                                       f"{pref}play ссылка")
    embed.add_field(name="prefix", value=f"Поменять префикс для команд. Пример: {pref}prefix новый_префикс")
    await ctx.send(embed=embed)


with open("token.txt") as file:
    token = file.read()
client.run(token)
