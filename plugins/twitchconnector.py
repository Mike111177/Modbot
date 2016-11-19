import irc3
from components import config, pluginmanager, abstracts
import asyncio
from threading import Thread

defaults = {"Twitch": {"Username": "", "OauthPass": "", "Channel": "", "Client-ID": ""}}

@irc3.plugin
class IRCPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        
    @irc3.event(irc3.rfc.CONNECTED)
    async def connected(self, **kw):
        await self.bot.send_line("CAP REQ :twitch.tv/tags")
        pluginmanager.runEvent("TWITCH:CONNECTED")
    
    
    @irc3.event(irc3.rfc.PRIVMSG)
    async def prvmsg(self, event=None, mask=None, tags=None, **kw):
        if tags:
            kw['tags'] = irc3.tags.decode(tags)
        kw['nick'] = mask.nick
        pluginmanager.runEvent("TWITCH:MSG", **kw)


class Plugin(abstracts.Plugin):
    
    def __init__(self):
        Connector()

class Connector(Thread):
    
    def __init__(self):
        Thread.__init__(self, name="TwitchIRC_Async_Connector")
        self.start()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.cfg = config.load("twitch", defaults)["Twitch"]
        self.setup = dict(
            autojoins=[self.cfg["Channel"]],
            host='irc.twitch.tv', port=6667,
            username=self.cfg["Username"], password=self.cfg["OauthPass"], nick=self.cfg["Username"],
            ssl=False,
            includes=[__name__],
            loop=self.loop)
        self.bot = irc3.IrcBot(**self.setup)
        rec = {"BOT":self.bot,"LOOP":self.loop,"CLI-ID":self.cfg["Client-ID"]}
        pluginmanager.addresource("TWITCH", rec)
        self.bot.run(forever=True)
