from time import clock

import discord, configparser, irc3, asyncio, urllib, traceback

from heuristics import isSpamBot
from nooblist import getNooblist
from datetime import datetime, timedelta
from math import floor

def load():
    config = configparser.ConfigParser()
    config.read("Configuration.ini")
    if "Twitch" not in config:
        config["Twitch"] = {"Username": "", "OauthPass": "", "Channel": "", "Client-ID": ""}
    if "Discord" not in config:
        config["Discord"] = {"Token" : "", "Banlist_Channel": "", "Interface_Channel": ""}
    save(config)
    return config

def save(config):
    with open("Configuration.ini", "w") as configfile:
        config.write(configfile)

def runTwitchBot(user, password, host, port, channel, loop):

    config = dict(
        autojoins=[channel],
        host=host, port=port,
        username=user, password=password, nick=user,
        ssl=False,
        includes=[__name__],
        loop=loop)

    bot = irc3.IrcBot(**config)
    bot.run(forever=False)
    return bot

@irc3.event(irc3.rfc.PRIVMSG)
async def ircmsg(bot, event=None, mask=None, target=None, data=None):
    try:
        spam, special, age = isSpamBot(mask.nick, data, config['Twitch']['Client-ID'])
        if spam:
            bot.privmsg(target, '.ban %s'%mask.nick)
            if not special:
                bot.privmsg(target, '.w %s Hello %s, you have been banned from this chat by our new experimental heuristics system. If you believe that you were wrongfully banned and would like to appeal please whisper one of the chat moderators. We are sorry for the inconvienence.'%(mask.nick, mask.nick))
                bot.privmsg(target, '.w %s Do not reply to this whisper.'%mask.nick)
            await disbot.send_message(disbot.get_channel(str(config['Discord']['Banlist_Channel'])),'%s: "%s" (Age: %s) (Special: %s)'%(mask.nick,data,str(timedelta(seconds=floor(age))),str(special)))
    except:
        print('Error in spambot filter.\nUser: %s\nMessage: "%s"'%(mask.nick,data))
        print(traceback.format_exc())
        return

loop = asyncio.get_event_loop()
disbot = discord.Client()
config = load()
twibot = runTwitchBot(config["Twitch"]["Username"], config["Twitch"]["OauthPass"], 'irc.twitch.tv', 6667, config["Twitch"]["Channel"], loop)
            

@disbot.event
async def on_ready():
    await disbot.change_presence(game=discord.Game(name='Duck Hunt'))
    print('Discord: Logged in as')
    print(disbot.user)
    print('------')

@disbot.event
async def on_message(message):
    try:
        #if str(message.channel) == 'modbot_chat_interface' and disbot.user!=message.author:
        #    await disbot.delete_message(message)
        #    try:
        #        twibot.privmsg(config["Twitch"]["Channel"], message.content)
        #        await disbot.send_message(message.channel, '%s: "%s" (Sent to EJs Chat)'%(message.author.mention, message.content))
        #    except:
        #        await disbot.send_message(message.channel, '%s: "%s" (Message Failed)'%(message.author.mention, message.content))
        if str(message.content).startswith('?nooblist'):
            t = clock()
            nubs = getNooblist(config['Twitch']['Channel'], config['Twitch']['Client-ID'])
            if len(nubs) is 0:
                out = 'No noobs found in chat :smile:'
            else:
                out = str(nubs)
            await disbot.send_message(message.channel,'%s [%fs]'%(out,clock()-t))
        elif str(message.content).startswith('?rotun') and len(str(message.content).split(' '))>1:
            string = ' '.join(str(message.content).split(' ')[1:])
            response = urllib.request.urlopen('http://thuum.org/translate-dragon.php?text=%s'%string.replace(" ","%20"))
            html = response.read()
            data  = html.decode("utf-8", errors="replace")
            await disbot.send_message(message.channel, data)
        elif str(message.content).startswith('?bancount'):
            args = str(message.content).split(' ')
            dtime = 1
            if len(args)>1:
                try:
                    dtime = float(args[1])
                except:
                    dtime = 1
            counter = 0
            async for m in disbot.logs_from(disbot.get_channel(str(config['Discord']['Banlist_Channel'])), limit=500, after=(datetime.utcnow()-timedelta(hours=dtime))):
                if m.author == disbot.user:
                    counter += 1
            await disbot.send_message(message.channel, 'There have been %d automated bans in the past %s hour(s).'%(counter, dtime))
        elif str(message.content).startswith('?weather'):
            await disbot.send_message(message.channel, 'Fuck you')

    except Exception as e:
        print(e)
        return


loop.create_task(disbot.start(config['Discord']['Token']))
loop.run_forever()