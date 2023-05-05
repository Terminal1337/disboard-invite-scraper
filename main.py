import tls_client
import json
import random
import time
import os
from colorama import Fore, Style,init
import threading
import datetime
import httpx
import ctypes

init(convert=True)
proxies = open("input/proxies.txt").read().splitlines()

total = 0
class Utils(object):
    @staticmethod
    def get_proxies(mode):
        if mode:
            return f'http://{random.choice(proxies)}'
        else:
            return None
    @staticmethod
    def code(session,server_id,token):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://disboard.org/",
            "Sec-Ch-Ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "x-csrftoken": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        r = session.post(f"https://disboard.org/site/get-invite/{server_id}", headers=headers, proxy=Utils.get_proxies())
        if r.status_code == 200:
            print(r.text)
        else:
            return False
    @staticmethod    
    def DebugInvite(code):
            r = httpx.get(f'https://discord.com/api/v10/invites/{code}').json()['guild']
            return r['verification_level']
    @staticmethod
    def UpdateTitle(msg):
        ctypes.windll.kernel32.SetConsoleTitleW(msg)


class Logger():
    @staticmethod
    def SaveServers(tag,disboard : bool = True,discord : bool = False,disboard_id : str = None, discord_invite : str = None):
        if disboard:
            with open(f'data/{tag}/disboard.txt','a') as f:
                f.write(disboard_id+'\n')
                f.close()
        if discord:
            with open(f'data/{tag}/discord.txt','a') as f:
                f.write(discord_invite+'\n')
                f.close()
    @staticmethod
    def print_log(status, serer_id,debug : str = None):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color1 = random.choice(
            [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN])
        color2 = random.choice(
            [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN])
        new = ''
        # color_message = f"{Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}"
        color_status = f"{color1}{status}{Style.RESET_ALL}"  
        color_id = f"{Fore.LIGHTBLACK_EX}[{serer_id}]{Style.RESET_ALL}"
        if debug is not None:
            color_debug = f"{color2}{debug}{Style.RESET_ALL}"      
        with threading.Lock():
            if debug is not None:
                print(f"{color2}[{timestamp}]{Fore.RESET} | {color_status} {color_id} {color_debug}")
                return
            print(f"{color2}[{timestamp}]{Fore.RESET} | {color_status} {color_id}")
    @staticmethod
    def saveErrors(error : str):
        with open('data/errors.txt','a',encoding='utf-8') as f:
            f.write(f"{error}\n")
            f.close() 

        
class Scraper():
    def __init__(self) -> None:
        with open("config.json") as f:
            self.config = json.load(f)
            f.close()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://disboard.org/",
            "Sec-Ch-Ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        self.success = 0
        self.fails = 0
        self.errors = 0
        self.proxy = self.config['proxy']['use_proxy']
        self.tag = self.config['settings']['tag']
        self.discord = self.config['settings']['discord_mode']
        self.limit = self.config['settings']['limit']
        self.debug = self.config['settings']['debug']
        self.cloudflare = self.config['cloudflare']['challenged']
        self.client = session = tls_client.Session(client_identifier="chrome112",random_tls_extension_order=True)
        if self.cloudflare:
            self.headers['User-Agent'] = self.config['cloudflare']['user_agent']
            self.headers["cookie"] = input("Cloudflare Cookie : ")
            self.proxy = False
        for i in range(self.limit):
            i += 1
            threading.Thread(target=self.scraper,args=(self.tag,str(i))).start()
        print(f"{Fore.GREEN}[DEBUG] Servers Found  : {self.success}{Fore.RESET}")

    def scraper(self, tag, count):
        try:
            if not os.path.exists(os.path.join('data/', tag)):
                os.makedirs(os.path.join('data/', tag))
            proxy = Utils.get_proxies(self.proxy)
            r = self.client.get(f"https://disboard.org/servers/tag/{tag}/{count}", headers=self.headers, proxy=proxy).text
            csrf = str(r).split('<meta name="csrf-token" content="')[1].split('">')[0]
            r = str(r).split('a href="/server/',9999)
        except Exception as e:
            Utils.UpdateTitle(f"Disboard Scraper | Success : {self.success} | Fails : {self.fails} | Errors : {self.errors} | Tag : {tag} | Limit : {self.limit}")
            Logger.saveErrors(str(e))
            self.errors += 1
            self.scraper(tag,count)
        try:

            for i in r:
                if "join" in i:
                    if "html" not in i:
                        if "report" not in i:
                            i = str(i.split('"')[0]).split('join/')[1]
                            if self.discord:
                                headers = self.headers; headers['x-csrf-token'] = csrf
                                resp = self.client.post(f'https://disboard.org/site/get-invite/{i}', headers=headers, proxy=proxy).text
                                if "discord" in resp:
                                    if self.debug:
                                        Logger.print_log(f"[SCRAPED]", resp,"| Verification : "+str(Utils.DebugInvite(str(resp).split('.gg/')[1].split('"')[0])))
                                    else:
                                        Logger.print_log(f"[SCRAPED]", resp)
                                    Logger.SaveServers(self.tag,False,True,None,str(resp).split('.gg/')[1].split('"')[0])
                                    self.success += 1
                                else:
                                    Logger.saveErrors(f"Error : {resp}")
                                    self.fails += 1
                            else:
                                Logger.print_log(f"[SCRAPED]", i)
                                Logger.SaveServers(self.tag,True,False,f"https://disboard.org/server/join/{i}",None)
                                self.success += 1
                            Utils.UpdateTitle(f"Disboard Scraper | Success : {self.success} | Fails : {self.fails} | Errors : {self.errors} | Tag : {tag} | Limit : {self.limit}")
        except:
            pass
        print(f"{Fore.GREEN}[DEBUG] Servers Found  : {self.success}{Fore.RESET}")

if __name__ == "__main__":
    Scraper()
    
    
