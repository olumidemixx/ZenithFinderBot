

def topTraders(contractAddresses):
    from traders import TopTraders
   
    topTraders = TopTraders()
    
    # Replace with your actual token address and API key
    
    data = topTraders.topTraderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data

def topHolders(contractAddresses):
    from holders import TopHolders
    
    topHolders = TopHolders()
    
    # Replace with your actual token address and API key
    
    data = topHolders.topHolderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data


def earlyBuyers(contractAddresses):
    from earlyBuyers import EarlyBuyers
    earlyBuyers = EarlyBuyers()
    # Replace with your actual token address and API key
    
    data = earlyBuyers.earlyBuyersdata(contractAddresses, threads = 40, useProxies = False, buyers = 30)
    

    #result = {key: 0 for key in data}
    return data

def single_topTraders(contractAddresses):
    from single_traders import TopTraders
   
    topTraders = TopTraders()
    
    # Replace with your actual token address and API key
    
    data = topTraders.topTraderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data

def single_topHolders(contractAddresses):
    from single_holders import TopHolders
    
    topHolders = TopHolders()
    
    # Replace with your actual token address and API key
    
    data = topHolders.topHolderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data
