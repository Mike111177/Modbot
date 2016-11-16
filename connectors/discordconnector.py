import discord
from components import config, pluginmanager
import asyncio

defaults = {"Discord": {
    "Token": ""}};

h = [];

async def on_ready():
    print('Logged in as')
    print(h[0].user.name)
    print(h[0].user.id)
    print('------')
    
async def on_message(message):
    pluginmanager.runEvent("DSC:MSG", message)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = discord.Client(loop=loop)
    bot.event(on_ready)
    bot.event(on_message)
    h.append(bot)
    token = config.load("discord", defaults)["Discord"]["Token"]
    loop.create_task(bot.start(token))
    loop.run_forever()
    
    