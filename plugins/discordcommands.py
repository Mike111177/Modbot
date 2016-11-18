from components import abstracts, pluginmanager
import asyncio
import pprint


class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler("DSC:MSG", self, self.proc, abstracts.Handler.PRIORITY_HIGH),
                abstracts.Handler("DSC:COMMAND:?COMMANDS", self, self.commands)]
    
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