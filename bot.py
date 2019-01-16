import discord
from discord.ext import commands

import logging
import time

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = 'NTM0ODU2NDAxMzc4NDc2MDQy.Dx_vkw.bIVvr5GumIe0XmOITL1yYzHS7NA'

act = discord.Activity(type=discord.ActivityType.watching, name="my master developping me UwU")
Barbote = commands.Bot(command_prefix="?!", description="Hello I'm Barbote !\n I'm useless at this point",
        activity=act)

@Barbote.event
async def on_ready():
    print('Logged in as')
    print(Barbote.user.name)
    print(Barbote.user.id)
    print('--------------')

@Barbote.event
async def on_message(message):
    if message.author.bot:
        return
    if type(message.channel) == discord.DMChannel or type(message.content) == discord.GroupChannel:
        m = "I received a message from : {0}#{1}\nIt said : {2}".format(message.author.name, message.author.discriminator, message.content)
        await Barbote.get_user(175392863587139584).dm_channel.send(m)

@Barbote.command()
async def ping(ctx):
    m = await ctx.send("Pong!")
    ms = (m.created_at-ctx.message.created_at).total_seconds() * 1000
    await m.edit(content='Pong! Latency : {}ms'.format(int(ms)))

try:
    Barbote.run(TOKEN)
except (HTTPException, LoginFailure) as e:
    Barbote.loop.run_until_complete(Barbote.logout())
    log.fatal(e)

