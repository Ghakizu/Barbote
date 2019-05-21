import discord
from discord.ext import commands
import logging
import asyncio
import os
import signal

# Stop the programm when a SIGTERM is received
def handle_sigterm(*args):
    raise KeyboardInterrupt()

signal.signal(signal.SIGTERM, handle_sigterm)

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

initial_extensions = ['cogs.owner', 'cogs.roles']

if __name__ == '__main__':
    for extension in initial_extensions:
        Barbote.load_extension(extention)

@Barbote.event
async def on_ready():
    print('Logged in as')
    print(Barbote.user.name)
    print(Barbote.user.id)
    print('--------------')

try:
    Barbote.loop.run_until_complete(Barbote.start(os.getenv('BARBOTETOKEN',
        None), bot=True, reconnect=True))
except KeyboardInterrupt as e:
    Barbote.loop.run_until_complete(Barbote.logout())
    log.fatal(e)
finally:
    Barbote.loop.close()
