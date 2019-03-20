import discord
from discord.ext import commands
import logging
import time
import database
import asyncio
import asyncpg
import os

log = logging.getLogger('discord')
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log',
        encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

activity_name = "gérer le serveur c'est compliqué un peu"
act = discord.Activity(type=discord.ActivityType.playing, name=activity_name)

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['>?', '?!']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


Barbote = commands.Bot(command_prefix="?!", description="""Hello I'm Barbote !\n
        I'm role management bot""",
        activity=act, owner_id=int(os.getenv('GHAKID', None)))

async def getallrows(connection):
    b = await database.is_table(connection)
    if b:
        r = await connection.fetch('SELECT * FROM categories;')
        return r 
    return None

conn = Barbote.loop.run_until_complete(database.connect())
if(conn is None):
    raise Exception("Can't connect to the database")
rows = Barbote.loop.run_until_complete(getallrows(conn))

@Barbote.event
async def on_ready():
    print('Logged in as')
    print(Barbote.user.name)
    print(Barbote.user.id)
    print('--------------')

@Barbote.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        await check(after, rows)
        await stafftestperms(after, before.roles, after.roles)

@Barbote.event
async def on_member_join(member):
    if member.bot:
        await botperms(member)

@Barbote.event
async def on_message(message):
    if message.author.bot:
        return
    if type(message.channel) == discord.DMChannel or type(message.content) ==  discord.GroupChannel:
        embed = discord.Embed()
        embed.title = message.content
        embed.timestamp = message.created_at
        embed.set_author(icon_url=message.author.avatar_url,
                name=str(message.author))
        embed.color = discord.Colour.dark_orange()
        if(not get_owner().dm_channel):
            await get_owner().create_dm()
        await get_owner().dm_channel.send(content="Message received!",
                embed=embed)
    await Barbote.process_commands(message)

@Barbote.event
async def on_command_error(ctx, error):
    await ctx.send("There is an error!\n{0}".format(error))
    log.error(error)

@Barbote.command()
async def ping(ctx):
    """Ping me
    """
    m = await ctx.send("Pong!")
    ms = (m.created_at-ctx.message.created_at).total_seconds() * 1000
    await m.edit(content='Pong! Latency : {}ms'.format(int(ms)))
    await ctx.send("Bot latency : {}ms".format(int(Barbote.latency * 1000))) 

@Barbote.command()
@commands.has_permissions(manage_roles=True)
async def setrole(ctx, cat:discord.Role, *roles:discord.Role):
    """Set a list of roles for a category of roles
    Usage : setrole category roles*
    """
    if cat is not None and len(roles) > 0:
        print("Number of roles to add : {}".format(len(roles)))
        for x in roles:
            print("{} : {}".format(x, x.id))
        print(cat)
        guild = ctx.guild
        if guild is not None:
            print(guild.name)
        else:
            print("Guild is None")
        try:
            async with ctx.channel.typing():
                await addroles(ctx, cat.id, roles)
            await ctx.send('Done!\n Roles added to the category {0}'.format(
                cat.name))
            rows = await getallrows(conn)
        except Exception as e:
            await ctx.send("Debug error : {0}".format(e))
            print(e)
            log.fatal(e)
    else:
        ctx.send("Error : Not enought argument")

@Barbote.command()
@commands.has_permissions(manage_roles=True)
async def checkuser(ctx, user:discord.Member):
    """Check and update an user
    Usage : checkuser user
    """
    await ctx.send("Checking {0}...".format(user.mention))
    async with ctx.channel.typing():
       r =  await check(user, rows)
    if r:
        await ctx.send('Done!')
    else:
        await ctx.send('There is an error\n Exit code : {0}'.format(r))

@Barbote.command()
@commands.is_owner()
async def checkall(ctx):
    """Check and update all the users
    Uasage : chackall
    """
    members = ctx.guild.members
    c = 0
    b = 0
    e = 0
    for member in members:
        try:
            await ctx.send('Checking {0}...'.format(member.mention))
            a = await check(member, rows)
            if(not a):
                b += 1
            c+= 1
        except Exception as s:
            await ctx.send('Failed to check {0}\n{1}'.format(member.mention, s))
            e += 1
            pass
    await ctx.send("""Done!\n Checked {} members succesfully\n{} Bots found\n
    Failed to check {} members""".format(c, b, e))

@Barbote.command()
@commands.is_owner()
async def say(ctx, channel:discord.TextChannel, *, message):
    await channel.send(message)

async def addroles(ctx, cat, roles):
    # Add in Postgresql
    b = await database.is_table(conn)
    if b == False:
        await database.create_table(conn)
    rolesid = []
    for role in roles:
        rolesid.append(role.id)
    await conn.execute('''
            INSERT INTO categories(cat, roles)
            VALUES($1, $2)
            ON CONFLICT (cat)
            DO UPDATE SET roles = array_merge(categories.roles, $2)''',
            cat, rolesid)
    log.info("")

async def check(user, rows):
    if user.bot:
        await botperms(user)
    roles = await getroles(user)
    i = 0
    b = True
    while i < len(rows) and b:
        rl = rows[i]
        j = 0
        l = rl[1]
        while j < len(l) and not l[j] in roles:
            j += 1
        if j >= len(l):
            if rl[0] in roles:
                # Delete cat of user's roles
                cat = user.guild.get_role(rl[0])
                s = 'Deleting {0} for {1}'.format(cat, user)
                log.info(s)
                await user.remove_roles(cat, reason="""This user have no roles 
                    from this categorie""")
                b = False
        else:
            if not (rl[0] in roles):
                # Add cat of user's roles
                cat = user.guild.get_role(rl[0])
                s = 'Adding {0} for {1}'.format(cat, user)
                log.info(s)
                await user.add_roles(cat, reason="""This user have roles 
                    from this categorie""")
                b = False
        i += 1
    return 1

async def botperms(bot):
    botrole = bot.guild.get_role(430147158331883523)
    if (not botrole in bot.roles):
        await bot.add_roles(botrole, reason="This is a bot")
        log.info("Added role {} to {}".format(botrole.name, bot.name))

async def getroles(user):
    roles = user.roles
    r = []
    for role in roles:
        r.append(role.id)
    return r

async def stafftestperms(user, before, after):
    testrole = user.guild.get_role(521377232858644491)
    modid = user.guild.get_channel(556901618835128470)
    animid = user.guild.get_channel(556615951005777920)
    s = "{} is not in training period".format(user.name)
    if (testrole in after and not testrole in before):
        s = "Overwriting permissions of {} during the training period".format(
                user.name)
        overwrite = discord.PermissionOverwrite(read_messages=False)
        await modid.set_permissions(user, overwrite=overwrite,
                reason=s)
        await animid.set_permissions(user, overwrite=overwrite, reason=s)
    elif (not testrole in after and testrole in before):
        s = "Deleting overwrite for {}. Training period is over".format(
                user.name)
        await modid.set_permissions(user, overwrite=None, reason=s)
        await animid.set_permissions(user, overwrite=None, reason=s)
    log.info(s)

def get_owner():
    return Barbote.get_user(Barbote.owner_id)

def get_barbotechannel():
    return Barbote.get_channel(534851504386080818)

try:
    Barbote.loop.run_until_complete(Barbote.start(os.getenv('BARBOTETOKEN',
        None), bot=True, reconnect=True))
except KeyboardInterrupt as e:
    Barbote.loop.run_until_complete(get_barbotechannel().send("I'm loging out!"))
    Barbote.loop.run_until_complete(Barbote.logout())
    log.fatal(e)
finally:
    Barbote.loop.run_until_complete(database.disconnect(conn))
    Barbote.loop.close()
