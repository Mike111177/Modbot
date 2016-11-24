import asyncio
from components import abstracts, pluginmanager

'''#The plugin manager will only load the plugin if the class name is Plugin, and it extends abstract.Plugin'''
class Plugin(abstracts.Plugin): 
    
    '''The first thing the plugin manager does after initializing the plugin is ask for these event handlers in a list.
    Here the only event is tagged DSC:COMMAND:?GITHUB, which will be triggered when someone types ?GITHUB in discord, 
    assuming the discordcommands plugin is installed'''
    def handlers(self): 
        return [abstracts.Handler('DSC:COMMAND:?GITHUB', self, self.command)]
    
    '''Because we defined this function as the function for the DSC:COMMAND:?GITHUB event, this function will trigger
    when anyone in discord types in ?github, assuming the discordcommands plugin is installed. The DSC:COMMAND:?GITHUB 
    event is triggered with several arguments, however for this operation only message argument is needed, so **kw is
    used to capture all unneeded arguments.'''
    def command(self, message=None, **kw):
        #The discord connector on loading provides these two resources to the plugin manager on start. They are required to interact with discord.
        bot = pluginmanager.resources["DSC"]["BOT"] 
        loop = pluginmanager.resources["DSC"]["LOOP"]
        #Because we are in a different thread than the async discord process, in order to interact with discord, we must wrap any commands to discord in a coroutine sent to the discord async loop.
        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, 'https://github.com/Mike111177/Modbot'), loop) 
        