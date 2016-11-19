from components import abstracts, pluginmanager
import asyncio


class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?FIND', self, self.command)]
    
    def command(self, message=None, args=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        if len(args)>0:
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, 'http://lmgtfy.com/?q=%s'%'+'.join(args)), loop)
        return True