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
    
    PRIORITY_MONITOR = 0
    PRIORITY_HIGH = 1
    PRIORITY_MED = 2
    PRIORITY_LOW = 3
    PRIORITY_MIN = 4
    PRIORITY_HOOK = 5
    
    def __init__(self, event, plugin, function, priority=PRIORITY_MED, **kw):
        self.priority = priority
        self.event = event
        self.plugin = plugin
        self.function = function
        for key in kw:
            setattr(self, key, kw[key])
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Handler(plugin=%s,function=%s)"%(self.plugin.__module__,self.function.__name__)
    
    def handle(self, args, kargs):
        return self.function(*args,**kargs)
    
    def __call__(self, *args, **kargs):
        return self.handle(args, kargs)
        