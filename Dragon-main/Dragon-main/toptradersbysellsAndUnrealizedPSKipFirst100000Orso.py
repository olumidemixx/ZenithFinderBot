

def topTraders(contractAddresses):
    from Dragon import TopTraders, BundleFinder, ScanAllTx, BulkWalletChecker, TopTraders, CopyTradeWalletFinder, TopHolders, EarlyBuyers
    topTraders = TopTraders()
    bundle = BundleFinder()
    scan = ScanAllTx()
    walletCheck = BulkWalletChecker()
    topTraders = TopTraders()
    copytrade = CopyTradeWalletFinder()
    topHolders = TopHolders()
    earlyBuyers = EarlyBuyers()
    # Replace with your actual token address and API key
    
    data = topTraders.topTraderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data

def topHolders(contractAddresses):
    from Dragon import TopTraders, BundleFinder, ScanAllTx, BulkWalletChecker, TopTraders, CopyTradeWalletFinder, TopHolders, EarlyBuyers
    topTraders = TopTraders()
    bundle = BundleFinder()
    scan = ScanAllTx()
    walletCheck = BulkWalletChecker()
    topTraders = TopTraders()
    copytrade = CopyTradeWalletFinder()
    topHolders = TopHolders()
    earlyBuyers = EarlyBuyers()
    # Replace with your actual token address and API key
    
    data = topHolders.topHolderData(contractAddresses, threads = 40, useProxies = False)
    

    #result = {key: 0 for key in data}
    return data


def earlyBuyers(contractAddresses):
    from Dragon import TopTraders, BundleFinder, ScanAllTx, BulkWalletChecker, TopTraders, CopyTradeWalletFinder, TopHolders, EarlyBuyers
    topTraders = TopTraders()
    bundle = BundleFinder()
    scan = ScanAllTx()
    walletCheck = BulkWalletChecker()
    topTraders = TopTraders()
    copytrade = CopyTradeWalletFinder()
    topHolders = TopHolders()
    earlyBuyers = EarlyBuyers()
    # Replace with your actual token address and API key
    
    data = earlyBuyers.earlyBuyersdata(contractAddresses, threads = 40, useProxies = False, buyers = 30)
    

    #result = {key: 0 for key in data}
    return data