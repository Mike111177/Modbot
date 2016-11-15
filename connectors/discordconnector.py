import discord
from components import config
import asyncio

defaults = {"Discord": {
    "Token": ""}};

h = [];

async def on_ready():
    print('Logged in as')
    print(h[0].user.name)
    print(h[0].user.id)
    print('------')

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = discord.Client(loop=loop)
    bot.event(on_ready)
    h.append(bot)
    token = config.load("discord", defaults)["Discord"]["Token"]
    loop.create_task(bot.start(token))
    loop.run_forever()
    
    