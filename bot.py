import discord
from discord.ext import commands
import logging
import time
import database
import asyncio
import asyncpg
import os

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

loop = asyncio.get_event_loop()

act = discord.Activity(type=discord.ActivityType.playing, name=" watching my master developping me UwU")
Barbote = commands.Bot(command_prefix="?!", description="Hello I'm Barbote !\n I'm useless at this point",
        activity=act)

Ghakid = 175392863587139584
Ghakizu = Barbote.get_user(Ghakid)

async def getallrows(connection):
    r = await connection.fetch('SELECT * FROM "429792212016955423";')
    return r 

conn = loop.run_until_complete(database.connect())
rows = loop.run_until_complete(getallrows(conn))

@Barbote.event
async def on_ready():
    print('Logged in as')
    print(Barbote.user.name)
    print(Barbote.user.id)
    print('--------------')

@Barbote.event
async def on_member_update(before, after):
    if not after.bot and before.roles != after.roles:
        await check(after, rows)

@Barbote.event
async def on_message(message):
    if message.author.bot:
        return
    if type(message.channel) == discord.DMChannel or type(message.content) == discord.GroupChannel:
        m = "I received a message from : {0}#{1}\nIt said : {2}".format(message.author.name, message.author.discriminator, message.content)
        await Barbote.Ghakizu.dm_channel.send(m)
    await Barbote.process_commands(message)

@Barbote.event
async def on_command_error(ctx, error):
    await ctx.send("There is an error!\n{0}".format(error))
    log.error(error)

@Barbote.command()
async def ping(ctx):
    m = await ctx.send("Pong!")
    ms = (m.created_at-ctx.message.created_at).total_seconds() * 1000
    await m.edit(content='Pong! Latency : {}ms'.format(int(ms)))

@Barbote.command()
@commands.has_permissions(manage_roles=True)
async def setrole(ctx, cat:discord.Role, *roles:discord.Role):
    if ctx.guild.id != 429792212016955423:
        await ctx.send('This command is not implemented for this server.')
    elif cat is not None and len(roles) > 0:
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
            logger.fatal(e)
    else:
        ctx.send("Error : Not enought argument")

@Barbote.command()
@commands.has_permissions(manage_roles=True)
async def checkuser(ctx, user:discord.Member):
    await ctx.send("Checking {0}...".format(user.mention))
    async with ctx.channel.typing():
       r =  await check(user, rows)
    if r:
        await ctx.send('Done!')
    else:
        await ctx.send('There is an error\n Exit code : {0}'.format(r))

@Barbote.command()
@commands.has_role(535096760389861396)
async def checkall(ctx):
    members = ctx.guild.members
    c = 0
    e = 0
    for member in members:
        try:
            await ctx.send('Checking {0}...'.format(member.mention))
            await check(member, rows)
            c += 1
        except Exception as s:
            await ctx.send('Failed to check {0}\n{1}'.format(member.mention, s))
            e += 1
            pass
    await ctx.send("""Done!\n Checked {0} members succesfully\n Failed to check {1}
            members""".format(c, e))

async def addroles(ctx, cat, roles):
    # Add in Postgresql
    b = await database.is_table(conn)
    print(b)
    if b == False:
        await database.create_table(conn)
    print('Inserting element...')
    rolesid = []
    for role in roles:
        rolesid.append(role.id)
    await conn.execute('''
            INSERT INTO "429792212016955423"(cat, roles)
            VALUES($1, $2)
            ON CONFLICT (cat)
            DO UPDATE SET roles = array_merge("429792212016955423".roles, $2)''',
            cat, rolesid)
    print('Inserted')

async def check(user, rows):
    if user.bot:
        raise Exception("{0} is a bot".format(user.mention))
    roles = await getroles(user)
    try:
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
                    # Delete cat to user's roles
                    cat = user.guild.get_role(rl[0])
                    print('Deleting {0} for {1}'.format(cat, user))
                    await user.remove_roles(cat, reason="""This user have no roles 
                        from this categorie""")
                    b = False
            else:
                if not rl[0] in roles:
                    # Add cat to user's roles
                    cat = user.guild.get_role(rl[0])
                    print('Adding {0} for {1}'.format(cat, user))
                    await user.add_roles(cat, reason="""This user have roles 
                        from this categorie""")
                    b = False
            i += 1
        return 1
    except Exception as e:
        print(e)
        return 0

async def getroles(user):
    roles = user.roles
    r = []
    for role in roles:
        r.append(role.id)
    return r

try:
    Barbote.run(os.environ['BARBOTETOKEN'], bot=True, reconnect=True)
except (HTTPException, LoginFailure) as e:
    Barbote.loop.run_until_complete(Barbote.logout())
    log.fatal(e)
finally:
    loop.run_until_complete(database.disconnect(conn))
