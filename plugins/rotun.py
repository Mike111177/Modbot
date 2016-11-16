from components import abstracts, pluginmanager
import asyncio
import urllib


class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:MSG', self, self.command)]
    
    def command(self, message):
        if message.content.startswith('?rotun')and len(str(message.content).split(' '))>1:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            string = ' '.join(str(message.content).split(' ')[1:])
            response = urllib.request.urlopen('http://thuum.org/translate-dragon.php?text=%s'%string.replace(" ","%20"))
            html = response.read()
            data  = html.decode("utf-8", errors="replace")
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, data), loop)