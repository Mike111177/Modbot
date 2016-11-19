import discord
from components import config, pluginmanager, abstracts
import asyncio
from threading import Thread

defaults = {"Discord": {
    "Token": ""}};

class Plugin(abstracts.Plugin):
    
    def __init__(self):
        Connector()

class Connector(Thread):
    
    def __init__(self):
        Thread.__init__(self, name="Discord_Async_Connector")
        self.start()
    
    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')
        pluginmanager.runEvent("DSC:READY")
    
    async def on_message(self, message):
        pluginmanager.runEvent("DSC:MSG", message)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = discord.Client(loop=self.loop)
        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)
        token = config.load("discord", defaults)["Discord"]["Token"]
        self.loop.create_task(self.bot.start(token))
        rec = {"BOT":self.bot,"LOOP":self.loop}
        pluginmanager.addresource("DSC", rec)
        self.loop.run_forever()