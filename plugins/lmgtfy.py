import asyncio, argparse
from components import abstracts, pluginmanager

parse = argparse.ArgumentParser(description='Returns a nifty link to suit any of your needs.', add_help=False, prog='?find')
parse.add_argument('query', metavar='Q', nargs='*', help='Your search query.')
parse.add_argument('-s', '--short', action='store_true', help='Shortens link for easier use. (Not supported yet)')

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?FIND', self, self.command, parse=parse)]
    
    def command(self, message=None, pargs=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        if len(pargs['query'])>0:
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, 'http://lmgtfy.com/?q=%s'%'+'.join(pargs['query'])), loop)
        return True