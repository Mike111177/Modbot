import irc3
from components import config
import asyncio

defaults = {"Twitch": {"Username": "", "OauthPass": "", "Channel": "", "Client-ID": ""}}


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
    bot.run(forever=True)