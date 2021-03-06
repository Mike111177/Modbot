import discord, asyncio
from components import config, pluginmanager, abstracts
from threading import Thread, Lock

defaults = {"Discord": {
    "Token": ""}};

class Plugin(abstracts.Plugin):
    
    def __init__(self):
        self.connector = Connector()
        
    def unload(self):
        asyncio.run_coroutine_threadsafe(self.connector.bot.logout(), self.connector.loop).result()
        self.connector.loop.stop()
        self.connector.lock.acquire()
        self.connector.lock.release()
        self.connector.loop.close()
        del self.connector
        
    def handlers(self):
        return [abstracts.Handler("STATUS", self, self.status, priority=abstracts.Handler.PRIORITY_HOOK)]
    
    def status(self):
        if self.connector.bot.is_logged_in:
            stat = 'Logged in. Servers: %d.'%len(self.connector.bot.servers)
        else:
            stat = 'Disconnected.'
        return 'Discord Connector: %s'%stat

class Connector(Thread):
    
    def __init__(self):
        Thread.__init__(self, name="Discord_Async_Connector")
        self.start()
    
    async def on_ready(self):
        print('Logged into discord as: %s (%s)'%(self.bot.user.name,self.bot.user.id))
        pluginmanager.runEvent("DSC:READY")
    
    async def on_message(self, message):
        pluginmanager.runEvent("DSC:MSG", message)
        
    async def on_message_edit(self, before, after):
        if before.pinned and not after.pinned:
            pluginmanager.runEvent("DSC:UNPIN", after)
        elif after.pinned and not before.pinned:
            pluginmanager.runEvent("DSC:PIN", after)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = discord.Client(loop=self.loop)
        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)
        self.bot.event(self.on_message_edit)
        token = config.load("discord", defaults)["Discord"]["Token"]
        self.loop.create_task(self.bot.start(token))
        rec = {"BOT":self.bot,"LOOP":self.loop}
        pluginmanager.addresource("DSC", rec)
        self.lock = Lock()
        with self.lock:
            self.loop.run_forever()
        
        
        