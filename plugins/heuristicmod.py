from components import abstracts, pluginmanager, config
from math import floor
from datetime import timedelta
import traceback
import asyncio

defaults = {"Reporting": {"Channel": ""}}
cfg = config.load("name", defaults)

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('TWITCH:MSG', self, self.ircmsg)]
    
    def ircmsg(self, nick=None, target=None, data=None, **kw):
        cid = pluginmanager.resources["TWITCH"]["CLI-ID"]
        try:
            spam, special, age = isSpamBot(nick, data, cid)
            if spam:
                bot = pluginmanager.resources["TWITCH"]["BOT"]
                disbot = pluginmanager.resources["DSC"]["BOT"]
                loop = pluginmanager.resources["DSC"]["LOOP"]
                bot.privmsg(target, '.ban %s'%nick)
                if not special:
                    bot.privmsg(target, '.w %s Hello %s, you have been banned from this chat by our new experimental heuristics system. If you believe that you were wrongfully banned and would like to appeal please whisper one of the chat moderators. We are sorry for the inconvienence.'%(nick, nick))
                    bot.privmsg(target, '.w %s Do not reply to this whisper.'%nick)
                asyncio.run_coroutine_threadsafe(disbot.send_message(disbot.get_channel(str(cfg['Reporting']['Channel'])),'%s: "%s" (Age: %s) (Special: %s)'%(nick,data,str(timedelta(seconds=floor(age))),str(special))), loop)
        except:
            print('Error in spambot filter.\nUser: %s\nMessage: "%s"'%(nick,data))
            print(traceback.format_exc())
            return