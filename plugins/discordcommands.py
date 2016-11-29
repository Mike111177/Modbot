import asyncio, pprint
from components import abstracts, pluginmanager

helphelp = {"Content": "Bro really, you need help with the help command?"}
commandshelp = {"Content": "List all loaded commands."}

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler("DSC:MSG", self, self.proc, abstracts.Handler.PRIORITY_HIGH),
                abstracts.Handler("DSC:COMMAND:?COMMANDS", self, self.commands, help=commandshelp),
                abstracts.Handler("DSC:COMMAND:?HELP", self, self.helpcommand, help=helphelp)]
    
    def proc(self, message):
        if message.content.startswith('?') and message.author is not pluginmanager.resources["DSC"]['BOT'].user:
            parts = message.content.split(' ')
            args = parts[1:]
            command = parts[0]
            pluginmanager.runEvent('DSC:COMMAND:%s'%command.upper(), args=args, message=message, command=command.lower())
            return True
        
    def commands(self, message=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        cmds = []
        for x in pluginmanager.handlers:
            if x.startswith('DSC:COMMAND:'):
                cmds.append(x.split(':')[-1])
        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, "```\n%s\n```"%pprint.pformat(cmds, indent=2, width=20)), loop)
        
    def getCommand(self, command):
        command = command.upper()
        for x in pluginmanager.handlers:
            if x.startswith('DSC:COMMAND:') and x.split(':')[-1]==command:
                for pri in pluginmanager.handlers[x]:
                    for handler in pluginmanager.handlers[x][pri]:
                        return handler
        return None
    
    def getHelp(self, command):
        command = self.getCommand(command)
        if command and hasattr(command, 'help'):
                return command.help
        return None
        
    def helpcommand(self, message=None, args=None, **kw):
        if len(args)>0:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            helpinfo = self.getHelp(args[0])
            if helpinfo:
                asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, '```%s: %s```'%(args[0].upper(), helpinfo["Content"])), loop)
            else:
                asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, 'No help data found for `%s`.'%args[0].upper()), loop)
        return True
                                                 
            
            