'''
Created on Nov 15, 2016

@author: Mike
'''
class Plugin(object):
    
    def __init__(self, pluginmanager):
        self.plm = pluginmanager
        
    def load(self):
        pass
    
    def unload(self):
        pass
        
    def getEventListeners(self):
        return {}