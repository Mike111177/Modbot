from components import abstracts, pluginmanager, config
import asyncio
from time import clock

defaults = {"Chat": {"Channel": "", "Client-ID": ""}}
cfg = config.load("chatanalytics", defaults)



class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:MSG', self, self.command)]
    
    def command(self, message):
        if message.content.startswith('?nooblist'):
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            t = clock()
            nubs = getNooblist(cfg['Chat']['Channel'], cfg['Chat']['Client-ID'])
            if len(nubs) is 0:
                out = 'No noobs found in chat :smile:'
            else:
                out = str(nubs)
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s [%fs]'%(out,clock()-t)), loop) 