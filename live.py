import requests
import html.parser
from ws4py.client.threadedclient import WebSocketClient
import json
import threading

class Livethread(WebSocketClient):
    #argumentos precedidos de c_ sao funcoes de callback
    def __init__(self, c_livemsg):
        print('init live')
        self.c_msg = c_livemsg
        
        self.USER = 'somereddituser'
        self.PASS = 'somepassword'
        self.CLIENT_ID = 'someclientid'
        self.CLIENT_SECRET = 'someclientsecret'
        self.LIVETHREAD = 'somelivethread'
        
        self.modhash = ''
        self.access_token = ''
        self.user_agent = 'some user agent'
        self.login()
        self.websocket_url = self.get_websocket()
        WebSocketClient.__init__(self,self.websocket_url)

    def login(self):
        #get modhash
        login_data = {'user':self.USER,'passwd':self.PASS,'api_type':'json'}
        response = requests.post(r'https://www.reddit.com/api/login', data=login_data, headers={'user-agent':self.user_agent})
        self.modhash = response.json()['json']['data']['modhash']
        
        #oauth login
        client_auth = requests.auth.HTTPBasicAuth(self.CLIENT_ID,self.CLIENT_SECRET)
        post_data = {'grant_type':'password','username':self.USER,'password':self.PASS}
        headers = {'user-agent':self.user_agent}
        response = requests.post(r'https://ssl.reddit.com/api/v1/access_token', auth=client_auth, data=post_data, headers=headers)
        self.access_token = 'bearer ' + response.json()['access_token']
        
        threading.Timer(3590,self.login,()).start()

    def send_msg(self,msg):
        print('send msg live')
        livethread_post = r'https://oauth.reddit.com/api/live/' + self.LIVETHREAD + r'/update'
        msgdata = {'api_type':'json','body':msg,'x-modhash':self.modhash}
        msgheaders = {'user-agent':self.user_agent,'Authorization':self.access_token}
        response = requests.post(livethread_post,data=msgdata,headers=msgheaders)
        print(response.json())
        
    def get_websocket(self):
        response = requests.get(r'https://www.reddit.com/live/' + self.LIVETHREAD + r'/about.json',headers={'user-agent':self.user_agent})
        return html.parser.HTMLParser().unescape(response.json()['data']['websocket_url'])
        
    #WebSocketClient overload
    def received_message(self,m):
        jdict = json.loads(m.data.decode('utf-8',errors='replace'))
        if jdict['type'] == 'update':
            author = jdict['payload']['data']['author']
            message = jdict['payload']['data']['body']
            self.c_msg({'author':author,'message':message})
            try:
                print({'author':author,'message':message})
            except UnicodeEncodeError:
                print('received unprintable chars')

    def start(self):
        self.connect()
        print('live started')
        self.run_forever()
        
def livemsg(argdict):
    print('received')
        
if __name__ == '__main__':
    live = Livethread(livemsg)
    live.start()