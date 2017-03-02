import irc3, websocket, json, time, asyncio
from components import config, pluginmanager, abstracts
from threading import Thread, Lock

defaults = {"Twitch": {"Username": "", "OauthPass": "", "Channel": "","Channel-ID": "", "User-ID": "", "Client-ID": ""}}
cfg = config.load("twitch", defaults)["Twitch"]
notice = irc3.rfc.raw.new('NOTICE', r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>(NOTICE|HOSTTARGET|CLEARCHAT|USERSTATE|RECONNECT|ROOMSTATE|USERNOTICE)) (?P<channel>\S+)(\s+:(?P<data>.*)|$)')
modtopic = "chat_moderator_actions.%s.%s"%(cfg['User-ID'],cfg['Channel-ID'])

@irc3.plugin
class IRCPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        
    @irc3.event(irc3.rfc.CONNECTED)
    async def connected(self, **kw):
        await self.bot.send_line("CAP REQ :twitch.tv/tags")
        await self.bot.send_line("CAP REQ :twitch.tv/membership")
        await self.bot.send_line("CAP REQ :twitch.tv/commands")
        self.bot.join(cfg['Channel'])
        pluginmanager.runEvent("TWITCH:CONNECTED")
    
    
    @irc3.event(irc3.rfc.PRIVMSG)
    async def prvmsg(self, event=None, mask=None, tags=None, **kw):
        if tags:
            kw['tags'] = irc3.tags.decode(tags)
        kw['nick'] = mask.nick
        pluginmanager.runEvent("TWITCH:MSG", **kw)
        
    @irc3.event(notice)
    async def rnotice(self, event=None, tags=None, **kw):
        kw['notice'] = event
        if tags:
            kw['tags'] = irc3.tags.decode(tags)
        pluginmanager.runEvent("TWITCH:NOTICE", **kw)

class Plugin(abstracts.Plugin):
    
    def __init__(self):
        initlock = Lock()
        initlock.acquire()
        self.connector = IRCConnector(initlock)
        with initlock:
            self.bot = self.connector.bot
            self.loop = self.connector.loop
        self.pubsub = PubSubConnector()
        self.pubsub.start()
        
    def handlers(self):
        return [abstracts.Handler("STATUS", self, self.status, priority=abstracts.Handler.PRIORITY_HOOK)]
    
    def status(self):
        if self.pubsub.ws.sock.connected:
            pubsub='Connected'
        else:
            pubsub='Disconnected'
        if self.bot.protocol.closed:
            irc='Disconnected'
        else:
            irc='Connected'
        return 'Twitch Connector: IRC(%s), PUBSUB(%s)'%(irc,pubsub)
    
    def nick(self):
        return cfg["Username"]

class IRCConnector(Thread):
    
    def __init__(self, initlock):
        Thread.__init__(self, name="TwitchIRC_Async_Connector")
        self.initlock = initlock
        self.start()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.setup = dict(
            autojoins=[],
            host='irc.twitch.tv', port=6667,
            username=cfg["Username"], password=cfg["OauthPass"], nick=cfg["Username"],
            ssl=False,
            includes=[__name__,'irc3.plugins.userlist'],
            loop=self.loop)
        self.bot = irc3.IrcBot(**self.setup)
        rec = {"BOT":self.bot,"LOOP":self.loop,"CLI-ID":cfg["Client-ID"]}
        pluginmanager.addresource("TWITCH", rec)
        self.initlock.release()
        self.bot.run(forever=True)

class PubSubConnector(Thread):
    
        def __init__(self):
            Thread.__init__(self, name="TwitchPubSub_Syncronious_Connector")
            Thread(target=self.pingLoop, name="TwitchPubSub_PingLoop").start()
            
        def pingLoop(self):
            self.running = True
            time.sleep(5)
            while self.running:
                self.send({'type':'PING'})
                time.sleep(270)
            
        def run(self):
            self.ws = websocket.WebSocketApp("wss://pubsub-edge.twitch.tv",
                            on_message = self.on_message,
                            on_open=self.on_open,
                            on_close=self.run)
            self.ws.run_forever()
        
        def send(self, ddict):
            self.ws.send(json.dumps(ddict))      
        
        def on_open(self, args):
            self.send({"type":"LISTEN",
                       "data": {
                           "topics": [modtopic],
                           "auth_token": cfg["Oauth"]}})
            print('Connected to Twitch PubSub')
            
        def on_message(self, ws, data):
            ind = json.loads(data)
            if 'data' in ind:
                if 'topic' in ind['data']:
                    if ind['data']['topic']==modtopic:
                        actdict = json.loads(ind['data']['message'])
                        pluginmanager.runEvent("TWITCH:MOD:%s"%actdict['data']['moderation_action'].upper(), twitchchannel=cfg['Channel'], **actdict['data'])
                        pluginmanager.runEvent("TWITCH:MOD", twitchchannel=cfg['Channel'], **actdict['data'])