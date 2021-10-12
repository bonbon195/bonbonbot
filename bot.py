import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import youtube_dl
<<<<<<< Updated upstream
from youtube_dl import YoutubeDL
=======
import asyncio
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    print("chilling as {0.user}".format(client))


class MusicCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = {}
        self.music_queue = {}
        self.ydl_opts = {'ignoreerrors': True,
                         'format': 'bestaudio/best',
                         'noplaylist': True}
        self.FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                            'options': '-vn'}

        self.vc = {}

    def search_yt(self, item):
        with YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
            except TypeError:
                return False
            except Exception:
                return False
            return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self, ctx):
        if not ctx.guild.id in self.music_queue:
            self.music_queue[ctx.guild.id] = []
        if len(self.music_queue[ctx.guild.id]) > 0:
            self.is_playing[ctx.guild.id] = True
            m_url = self.music_queue[ctx.guild.id][0][0]['source']

            self.music_queue[ctx.guild.id].pop(0)

            self.vc[ctx.guild.id].play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS),
                                       after=lambda e: self.play_next(ctx))
        else:
            self.is_playing[ctx.guild.id] = False

    async def play_music(self, ctx):
        if not ctx.guild.id in self.music_queue: self.music_queue[ctx.guild.id] = []
        if len(self.music_queue[ctx.guild.id]) > 0:
            self.is_playing[ctx.guild.id] = True

            m_url = self.music_queue[ctx.guild.id][0][0]['source']
            if not ctx.guild.id in self.vc or not self.vc[ctx.guild.id].is_connected():
                self.vc[ctx.guild.id] = await self.music_queue[ctx.guild.id][0][1].connect()
            else:
                try:
                    self.vc[ctx.guild.id] = await self.client.move_to(self.music_queue[ctx.guild.id][0][1])
                except AttributeError:
                    self.is_playing[ctx.guild.id] = False
                    return
            print(self.music_queue[ctx.guild.id])

            title = ""
            title += self.music_queue[ctx.guild.id][0][0]['title']
            embed = discord.Embed(title="",
                                  description=f":notes: Playing \n `{title}` \n - Now!\n [{ctx.author.mention}]",
                                  color=discord.Color(0xff3aab))
            await ctx.send(embed=embed)
            self.music_queue[ctx.guild.id].pop(0)

            self.vc[ctx.guild.id].play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS),
                                       after=lambda e: self.play_next(ctx))
        else:
            self.is_playing[ctx.guild.id] = False

    @commands.command()
    async def play(self, ctx, *args):
        if not ctx.guild.id in self.music_queue: self.music_queue[ctx.guild.id] = []
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send(f"Connect to a voice channel")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(f"This video is inappropriate or this is a playlist")
            else:
                self.music_queue[ctx.guild.id].append([song, voice_channel])
                title = ""
                title += self.music_queue[ctx.guild.id][0][0]['title']
                embed = discord.Embed(title="",
                                      description=f":pencil: Added song: \n `{title}` \n - To queue! \n "
                                                  f"[{ctx.author.mention}]",
                                      color=discord.Color(0xff3aab))
                await ctx.send(embed=embed)
                if not ctx.guild.id in self.is_playing or self.is_playing[ctx.guild.id] == False:
                    await self.play_music(ctx)

    @commands.command()
    async def queue(self, ctx):
        if not ctx.guild.id in self.music_queue: self.music_queue[ctx.guild.id] = []
        retval = ""
        for i in range(0, len(self.music_queue[ctx.guild.id])):
            retval += "`" + self.music_queue[ctx.guild.id][i][0]['title'] + "`" + "\n"
        print(retval)
        if retval != "":
=======
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
>>>>>>> Stashed changes
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


<<<<<<< Updated upstream
    @commands.command()
    async def leave(self, ctx):
        if self.vc[ctx.guild.id].is_connected():
            await self.vc[ctx.guild.id].disconnect()
            self.is_playing[ctx.guild.id] = False
            if not ctx.guild.id in self.music_queue:
                self.music_queue[ctx.guild.id] = []
            self.music_queue[ctx.guild.id].clear()

    @commands.command()
    async def pause(self, ctx):
        if self.is_playing[ctx.guild.id]:
            self.vc[ctx.guild.id].pause()
        else:
            await ctx.send("No audio is playing")

    @commands.command()
    async def resume(self, ctx):
        if self.vc[ctx.guild.id].is_paused():
            self.vc[ctx.guild.id].resume()
        else:
            await ctx.send("Audio is not paused")

    @commands.command()
    async def stop(self, ctx):
        self.is_playing[ctx.guild.id] = False
        self.vc[ctx.guild.id].stop()

    @commands.command()
    async def clear(self, ctx):
        if not ctx.guild.id in self.music_queue:
            self.music_queue[ctx.guild.id] = []
        self.music_queue[ctx.guild.id].clear()
        self.is_playing[ctx.guild.id] = False
        embed = discord.Embed(title="",
                              description=f"Queue is cleared. [{ctx.author.mention}]",
                              color=discord.Color(0xff3aab))
        await ctx.send(embed=embed)


client.add_cog(MusicCog(client))
=======

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            queues[ctx.guild.id].clear()
            voice.stop()
    except:
        AttributeError


>>>>>>> Stashed changes

with open("token.txt") as file:
    token = file.read()
client.run(token)
