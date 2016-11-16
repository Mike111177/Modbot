import irc3
from components import config, pluginmanager
import asyncio

defaults = {"Twitch": {"Username": "", "OauthPass": "", "Channel": "", "Client-ID": ""}}


@irc3.event(irc3.rfc.CONNECTED)
async def connected(bot, **kw):
    await bot.send_line("CAP REQ :twitch.tv/tags")
    
    
@irc3.event(irc3.rfc.PRIVMSG)
async def prvmsg(bot, event=None, mask=None, **kw):
    kw['tags'] = irc3.tags.decode(kw['tags'])
    kw['nick'] = mask.nick
    pluginmanager.runEvent("TWIRC:MSG", **kw)

def run():
    loop = asyncio.new_event_loop()
    cfg = config.load("twitch", defaults)["Twitch"]
    setup = dict(
        autojoins=[cfg["Channel"]],
        host='irc.twitch.tv', port=6667,
        username=cfg["Username"], password=cfg["OauthPass"], nick=cfg["Username"],
        ssl=False,
        includes=[__name__],
        loop=loop)
    bot = irc3.IrcBot(**setup)
    rec = {"BOT":bot,"LOOP":loop,"CLI-ID":cfg["Client-ID"]}
    pluginmanager.addresource("TWITCH", rec)
    bot.run(forever=True)