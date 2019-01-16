import discord
import asyncio
import logging
import function

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = 'NTM0ODU2NDAxMzc4NDc2MDQy.Dx_vkw.bIVvr5GumIe0XmOITL1yYzHS7NA'
prefix = '*'

class Barbote(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

client = Barbote()
client.run(TOKEN)
