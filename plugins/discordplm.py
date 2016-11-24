import asyncio, pprint, traceback
from components import abstracts, pluginmanager, config


defaults = {"Administration": {"Admin": ""}}
cfg = config.load("discordplm", defaults)

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?PLM', self, self.command)]
    
    def command(self, message=None, args=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"] 
        loop = pluginmanager.resources["DSC"]["LOOP"]
        if len(args)>0:
            if str(message.author.id)==cfg["Administration"]["Admin"]:
                if args[0]=='unload' and len(args)>1:
                    try:
                        pluginmanager.unloadPlugin(args[1])
                        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, ':thumbsup:'), loop)
                    except RuntimeError:
                        pass
                    else:
                        traceback.print_exc()
                        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, ':thumbsdown:'), loop)
                elif args[0]=='reload' and len(args)>1:
                    try:
                        pluginmanager.reloadPlugin(args[1])
                        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, ':thumbsup:'), loop)
                    except:
                        traceback.print_exc()
            else:
                asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, 'You don\'t have permission for that.'), loop)
        else:
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, pprint.pformat(pluginmanager.plugins.keys(), indent=2, width=40)), loop)