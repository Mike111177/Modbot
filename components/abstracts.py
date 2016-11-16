'''
Created on Nov 15, 2016

@author: Mike
'''
class Plugin(object):
        
    def load(self):
        pass
    
    def unload(self):
        pass
        
    def handlers(self):
        return []
    
class Handler(object):
    
    PRIORITY_MAX = 0
    PRIORITY_HIGH = 1
    PRIORITY_MED = 2
    PRIORITY_LOW = 3
    PRIORITY_MIN = 4
    
    def __init__(self, event, plugin, function, priority=PRIORITY_MED):
        self.priority = priority
        self.event = event
        self.plugin = plugin
        self.function = function
        
    def handle(self, args, kargs):
        return self.function(*args,**kargs)
        