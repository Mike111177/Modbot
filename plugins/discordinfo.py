import asyncio
from components import abstracts, pluginmanager

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?DISINFO', self, self.command)]
    
    def command(self, message=None, args=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        if len(args)>0:
            if args[0].lower()=='channelid':
                asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, str(message.channel.id)), loop)    
        