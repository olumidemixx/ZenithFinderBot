import json
import tls_client
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time
import random
import logging

ua = UserAgent(os='linux', browsers=['firefox'])

class TopHolders:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.allData = {}
        self.allAddresses = set()
        self.addressFrequency = defaultdict(int)
        self.totalTraders = 0
        self.proxyPosition = 0

    def randomise(self):
        self.identifier = random.choice([browser for browser in tls_client.settings.ClientIdentifiers.__args__ if browser.startswith(('chrome', 'safari', 'firefox', 'opera'))])
        self.sendRequest = tls_client.Session(random_tls_extension_order=True, client_identifier=self.identifier)

        parts = self.identifier.split('_')
        identifier, version, *rest = parts
        other = rest[0] if rest else None
        
        os = 'windows'
        if identifier == 'opera':
            identifier = 'chrome'
        elif version == 'ios':
            os = 'ios'
        else:
            os = 'windows'

        self.user_agent = UserAgent(browsers=[identifier], os=[os]).random

        self.headers = {
            'Host': 'gmgn.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.user_agent
        }

    def loadProxies(self):
        with open("Dragon/data/Proxies/proxies.txt", 'r') as file:
            proxies = file.read().splitlines()

        formatted_proxies = []
        for proxy in proxies:
            if ':' in proxy:  
                parts = proxy.split(':')
                if len(parts) == 4:
                    ip, port, username, password = parts
                    formatted_proxies.append({
                        'http': f"http://{username}:{password}@{ip}:{port}",
                        'https': f"http://{username}:{password}@{ip}:{port}"
                    })
                else:
                    formatted_proxies.append({
                        'http': f"http://{proxy}",
                        'https': f"http://{proxy}"
                    })
            else:
                formatted_proxies.append(f"http://{proxy}")        
        return formatted_proxies

    def configureProxy(self, proxy):
        if isinstance(proxy, dict): 
            self.sendRequest.proxies = {
                'http': proxy.get('http'),
                'https': proxy.get('https')
            }
        elif isinstance(proxy, str):
            self.sendRequest.proxies = {
                'http': proxy,
                'https': proxy
            }
        else:
            self.sendRequest.proxies = None
        return proxy
    
    def getNextProxy(self):
        proxies = self.loadProxies()
        proxy = proxies[self.proxyPosition % len(proxies)]
        self.proxyPosition += 1
        return proxy

    def getBondingCurve(self, contractAddress: str, useProxies):
        retries = 3
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}"

        for attempt in range(retries):
            self.randomise()
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                data = response.json().get('data', None)
                if data:
                    try:
                        bondingCurve = data['token']['pool_info']['pool_address']
                    except Exception:
                        bondingCurve = ""
                    return bondingCurve
            except Exception:
                print(f"[🐲] failed getbondingcurve function")
            time.sleep(1)
        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return ""


    def fetchTopHolders(self, contractAddress:str, useProxies = False):
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_holders/sol/{contractAddress}?orderby=amount_percentage&direction=desc"
        retries = 10
        
        time.sleep(5)
 
        for attempt in range(retries):
            self.randomise()
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                data = response.json().get('data', None)
                print("DATA VALUE")
                print(data)
                
                if data:
                    
                    return data
            except Exception as e:
                print(f"[🐲] failed fetchTopHolders function... {e}")
                    
            time.sleep(5)
        
        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return []

    def topHolderData(self, contractAddresses, threads= 40, useProxies = False):
        
        excludeAddress = ["5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"]

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.fetchTopHolders, address, useProxies): address for address in contractAddresses}

            for future in as_completed(futures):
                contract_address = futures[future]
                response = future.result()
                print("RESPONSE OF TOP HOLDERS")
                print(response)
                
                #bondingCurve = self.getBondingCurve(contract_address, useProxies)
                #print(f"bondingcurve{bondingCurve}")
                #excludeAddress.append(bondingCurve)
                self.allData[contract_address] = {}
                self.totalTraders += len(response)

                for top_trader in response:
                   
                    
                    if top_trader['address'] in excludeAddress or top_trader['cost_cur'] < 50:
                        continue

                    multiplier_value = top_trader['profit_change']
                    
                    if multiplier_value:
                        address = top_trader['address']
                        self.addressFrequency[address] += 1 
                        self.allAddresses.add(address)
                        
                        bought_usd = f"${top_trader['total_cost']:,.2f}"
                        total_profit = f"${top_trader['realized_profit']:,.2f}"
                        unrealized_profit = f"${top_trader['unrealized_profit']:,.2f}"
                        multiplier = f"{multiplier_value:.2f}x"
                        buys = f"{top_trader['buy_tx_count_cur']}"
                        sells = f"{top_trader['sell_tx_count_cur']}"
                        
                        self.allData[address] = {
                            "boughtUsd": bought_usd,
                            "totalProfit": total_profit,
                            "unrealizedProfit": unrealized_profit,
                            "multiplier": multiplier,
                            "buys": buys,
                            "sells": sells
                        }
        
        #repeatedAddresses = [address for address, count in self.addressFrequency.items() if count > 1]
        print("TOP HOLDERSSSS")
        #print(self.addressFrequency.items())
        
        repeatedAddresses = {address: count for address, count in self.addressFrequency.items() if count > 1}
        repeated_counts = [count for address, count in self.addressFrequency.items()]
        print(repeated_counts)

        
        return repeatedAddresses
    
    

def topHolders(contractAddresses):
    
    topHolders = TopHolders()
    
    # Replace with your actual token address and API key
    
    data = topHolders.topHolderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data