from asyncirc.ircbot import IRCBot
import threading
import queue
from live import Livethread

bothost = 'irc.somehost.org'
botchannel = '#somechannel'
botname = 'somenickname'
botpass = 'somepassword'
botident = 'someident'
botrealname = 'somerealname'

irc = IRCBot(host = bothost,
             nick=botname,
             ident=botident,
             realname=botrealname,
             password=botpass)

def livemsg(argdict):
    if botname != argdict['author']:
        messages = filter(None,argdict['message'].split('\n'))
        for paragraph in messages:
            irc.msg(botchannel, argdict['author'] + ': ' + paragraph)
             
live = Livethread(livemsg)

msgqueue = queue.Queue()
msgbuffer = queue.Queue()

@irc.on_join
def on_join(self, nick, host, channel):
    pass

@irc.on_msg
def on_msg(self, nick, host, channel, message):
    pass
        
@irc.on_chanmsg
def on_chanmsg(self, nick, host, channel, message):
    if nick == botname:
        return
    if message[0] != '.':
        return
    if not message[1:].strip():
        return
    msgbuffer.put('[{}]({}): {}'.format( nick, 'http://www.reddit.com/u/'+nick, message[1:] ))
    irc.msg('NickServ','ACC ' + nick)
        
@irc.on_privmsg
def on_privmsg(self,nick,host,message):
    pass
    
@irc.on_notice
def on_notice(self, nick, host, channel, message):
    if 'You are now identified' in message:
        irc.join(botchannel)

@irc.on_whois_start
def on_whois_start(self, nick):
    pass
    
@irc.on_whois_logged
def on_whois_logged(self, nick, msg):
    pass
    
@irc.on_whois_end
def on_whois_end(self, nick):
    pass

@irc.on_acc
def on_acc(self, nick, code):
    print('acc ' + nick + ': ' + code)
    if code == '3':
        msgqueue.put(msgbuffer.get())
    else:
        msgbuffer.get()
        irc.msg(botchannel,nick + ' is not logged in')
        
#executa de 2 em 2 segundos para enviar mensagens ao live thread, devido restricao da api do reddit
def empty_queue():
    text = ''
    try:
        text = msgqueue.get_nowait()
    except queue.Empty:
        pass
    if text:
        live.send_msg(text)
    threading.Timer(2,empty_queue,()).start()
    
if __name__ == '__main__':
    irc.start()
    empty_queue()
    live.start()

