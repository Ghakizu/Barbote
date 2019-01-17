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
dic = {}
Ghakid = 175392863587139584
Ghakizu = Barbote.get_user(Ghakid)

@Barbote.event
async def on_ready():
    print('Logged in as')
    print(Barbote.user.name)
    print(Barbote.user.id)
    print('--------------')

"""
@Barbote.event
async def on_message(message):
    if message.author.bot:
        return
    if type(message.channel) == discord.DMChannel or type(message.content) == discord.GroupChannel:
        m = "I received a message from : {0}#{1}\nIt said : {2}".format(message.author.name, message.author.discriminator, message.content)
        await Barbote.Ghakizu.dm_channel.send(m)
"""

@Barbote.command()
async def ping(ctx):
    m = await ctx.send("Pong!")
    ms = (m.created_at-ctx.message.created_at).total_seconds() * 1000
    await m.edit(content='Pong! Latency : {}ms'.format(int(ms)))

@Barbote.command()
async def setrole(ctx, rolesetted:discord.Role, *roles:discord.Role):
    print(len(roles))
    for x in roles:
        print("{} : {}".format(x, x.id))
    print(rolesetted)
    guild = ctx.guild
    if guild is not None:
        print(guild.name)
    else:
        print("Guild is None")
    try:
        async with ctx.channel.typing():
            c = addroles(rolesetted, roles)
        await ctx.send('Done!\n{0} roles added to the category {1}'.format(c,
            rolesetted.name))
        for key in dic.keys():
            print("{} : {}".format(guild.get_role(int(key)).name,
                guild.get_role(int(dic.get(key))).name))
    except Exception as e:
        await ctx.send("Wlh c'est cassé\nVoici l'erreur: {0}".format(e))
        print(e)
        logger.fatal(e)

@Barbote.command()
async def checkuser(ctx, user:discord.Member):
    ctx.send("Checking {0}...".format(user))
    async with ctx.channel.typing():
        // TODO
        ctx.send("Not yet implemented")

@Barbote.command()
async def checkall(ctx):
    // TODO
    ctx.send("Not yet implemented")

def addroles(rolesetted, roles):
    c = 0
    for role in roles:
        if not str(role.id) in dic:
            dic[str(role.id)] = str(rolesetted.id)
            c+=1
    return c

def check(user):
    // TODO
    pass

try:
    Barbote.run(TOKEN)
except (HTTPException, LoginFailure) as e:
    Barbote.loop.run_until_complete(Barbote.logout())
    log.fatal(e)

