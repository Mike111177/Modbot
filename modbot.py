from components.twitchconnector import TwitchConnector as TCon
from components.discordconnector import DiscordConnector as DCon
from threading import Thread

class TwitchRunner(Thread):
    def __init__(self, tcon):
        self.tcon = tcon
    
    def run(self):
        self.tcon.run()
        
class DiscordRunner(Thread):
    def __init__(self, tcon):
        self.tcon = tcon
    
    def run(self):
        self.tcon.run()
        
TwitchRunner(TCon()).start()
DiscordRunner(DCon()).start()