from components import abstracts, pluginmanager
import asyncio


class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:MSG', self, self.command)]
    
    def command(self, message):
        if message.content.startswith('?weather'):
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, 'Fuck You'), loop)    
        