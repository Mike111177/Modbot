import connectors.twitchconnector as TCon
import components.pluginmanager as plm
from threading import Thread

class TwitchRunner(Thread):
    def __init__(self, tcon):
        Thread.__init__(self, name="IRC_Async_Loop")
        self.tcon = tcon
    
    def run(self):
        self.tcon.run()
        
TwitchRunner(TCon).start()
plm.initialize()
