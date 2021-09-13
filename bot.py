import discord

client = discord.Client()


@client.event
async def on_ready():
    print("asadasd as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run('ODYyNzk4MTY1ODkxNzQzNzg1.YOdlaA.n1uO8QuRVhZ-8lW-SFcdwbYZyJs')
