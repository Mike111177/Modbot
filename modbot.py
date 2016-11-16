import connectors.twitchconnector as TCon
import connectors.discordconnector as DCon
import components.pluginmanager as plm
from threading import Thread

class TwitchRunner(Thread):
    def __init__(self, tcon):
        Thread.__init__(self, name="IRC_Async_Loop")
        self.tcon = tcon
    
    def run(self):
        self.tcon.run()
        
class DiscordRunner(Thread):
    def __init__(self, tcon):
        Thread.__init__(self, name="Discord_Async_Loop")
        self.tcon = tcon
    
    def run(self):
        self.tcon.run()
   
TwitchRunner(TCon).start()
DiscordRunner(DCon).start()
plm.initialize()
