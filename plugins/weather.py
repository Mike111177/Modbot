from components import abstracts


class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('DSC:MSG', self, self.command)]
    
    def command(self, message):
        if message.content.startswith('?weather'):
            print("Hi")
        