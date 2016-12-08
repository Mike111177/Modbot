import asyncio, argparse
from components import abstracts, pluginmanager

statparse = argparse.ArgumentParser(description='Displays debug status collected from plugins.', add_help=False, prog='?status')

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?STATUS', self, self.command, parse=statparse),
                abstracts.Handler('STATUS', self, self.status, priority=abstracts.Handler.PRIORITY_HOOK)]
    
    def command(self, message=None,**kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        msg = '```\n'
        for handler in pluginmanager.getHooks('STATUS'):
            msg = msg + handler() + '\n'
        msg = msg + '```'
        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, msg), loop)

        
    def status(self):
        return "Status Plugin: %d status providers."%len(pluginmanager.getHooks('STATUS'))