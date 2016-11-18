from components import abstracts, pluginmanager
import asyncio
import urllib


class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?ROTUN', self, self.command)]
    
    def command(self, message=None, args=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        string = ' '.join(args)
        response = urllib.request.urlopen('http://thuum.org/translate-dragon.php?text=%s'%string.replace(" ","%20"))
        html = response.read()
        data  = html.decode("utf-8", errors="replace")
        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, data), loop)