import discord
from components import config, pluginmanager
import asyncio

defaults = {"Discord": {
    "Token": ""}};

rec = {};

async def on_ready():
    print('Logged in as')
    print(rec["BOT"].user.name)
    print(rec["BOT"].user.id)
    print('------')
    
async def on_message(message):
    pluginmanager.runEvent("DSC:MSG", message)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = discord.Client(loop=loop)
    bot.event(on_ready)
    bot.event(on_message)
    token = config.load("discord", defaults)["Discord"]["Token"]
    loop.create_task(bot.start(token))
    rec = {"BOT":bot,"LOOP":loop}
    pluginmanager.addresource("DSC", rec)
    loop.run_forever()
    
    