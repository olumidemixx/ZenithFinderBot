import requests
import json
from datetime import datetime
from collections import defaultdict
import time
all_wallets = []
def find_best_traders(token_address, api_key, limit=100, skip_transactions=3000, max_pages=30):
    """
    Find the best traders for a specific Solana token using Helius API,
    starting after a specific number of transactions
    
    Args:
        token_address (str): The address of the Solana token to analyze
        api_key (str): Your Helius API key
        limit (int): Number of transactions to fetch per page
        skip_transactions (int): Number of transactions to skip before analyzing
        max_pages (int): Maximum number of pages to fetch after skipping
        
    Returns:
        list: Sorted list of traders by profits and holdings value
    """
    # Helius API endpoint
    url = f"https://api.helius.xyz/v0/addresses/{token_address}/transactions"
    
    # Parameters for the API request
    params = {
        "api-key": api_key,
        "limit": limit
    }
    
    # Skip to desired transaction position
    print(f"Skipping the first {skip_transactions} transactions...")
    before_param = None
    
    # Calculate how many pages to skip
    pages_to_skip = skip_transactions // limit
    remaining_to_skip = skip_transactions % limit
    
    # First, navigate to the approximate position by skipping full pages
    for page in range(pages_to_skip):
        if before_param:
            params["before"] = before_param
        
        if page % 10 == 0:  # Print status update every 10 pages
            print(f"Skipping page {page+1}/{pages_to_skip}...")
            
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            print(response.text)
            return []
        
        transactions = response.json()
        
        # Check if we hit the end
        if not transactions or len(transactions) == 0:
            print(f"Reached the end after {page} pages, there aren't {skip_transactions} transactions available")
            return []
        
        # Get the signature of the last transaction for pagination
        last_tx = transactions[-1]
        before_param = last_tx.get('signature')
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # If we have remaining transactions to skip in the last page
    if remaining_to_skip > 0 and before_param:
        params["before"] = before_param
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching final skipping page: {response.status_code}")
            return []
            
        transactions = response.json()
        
        if not transactions or len(transactions) == 0:
            print(f"Reached the end while skipping remaining transactions")
            return []
            
        # Get the signature of the last transaction at our desired starting point
        start_index = remaining_to_skip
        if len(transactions) > start_index:
            before_param = transactions[start_index].get('signature')
        else:
            before_param = transactions[-1].get('signature')
            
        time.sleep(0.5)
    
    print(f"Successfully skipped approximately {skip_transactions} transactions")
    print(f"Now collecting and analyzing transactions after this point...")
    
    # Now continue with collecting the transactions we want to analyze
    all_transactions = []
    
    for page in range(max_pages):
        if before_param:
            params["before"] = before_param
            
        print(f"Fetching page {page+1} for analysis after skipping")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            print(response.text)
            if page == 0:
                return []
            break
        
        transactions = response.json()
        
        if isinstance(transactions, dict) and "error" in transactions:
            print(f"API returned error: {transactions['error']}")
            if page == 0:
                return []
            break
            
        if not transactions or len(transactions) == 0:
            print("No more transactions found")
            break
            
        print(f"Fetched {len(transactions)} transactions")
        all_transactions.extend(transactions)
        
        if len(transactions) > 0:
            last_tx = transactions[-1]
            before_param = last_tx.get('signature')
        else:
            break
            
        time.sleep(0.5)
    
    print(f"Total transactions fetched for analysis: {len(all_transactions)}")
    
    if len(all_transactions) == 0:
        print("No transactions found for analysis after skipping.")
        return []
    
    # Track wallet positions and trades
    wallet_positions = defaultdict(lambda: {'amount': 0, 'cost_basis': 0})
    wallet_trades = defaultdict(list)
    wallet_stats = {}
    
    # Process each transaction
    for tx in all_transactions:
        try:
            # Extract transaction details
            timestamp = tx.get('timestamp', 0)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # Process token transfers in the transaction
            for tokenTransfer in tx.get('tokenTransfers', []):
                if tokenTransfer.get('mint') == token_address:
                    from_wallet = tokenTransfer.get('fromUserAccount')
                    to_wallet = tokenTransfer.get('toUserAccount')
                    amount = tokenTransfer.get('tokenAmount')
                    
                    if not from_wallet or not to_wallet or amount is None:
                        continue
                    
                    # Estimate the transaction value using available data
                    value = 0
                    for nativeTransfer in tx.get('nativeTransfers', []):
                        if nativeTransfer.get('fromUserAccount') == to_wallet or nativeTransfer.get('toUserAccount') == from_wallet:
                            value = nativeTransfer.get('amount', 0)
                            break
                    
                    # Record the trade
                    if from_wallet != 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': # Not a mint
                        # Seller is sending tokens out
                        previous_amount = wallet_positions[from_wallet]['amount']
                        previous_cost = wallet_positions[from_wallet]['cost_basis']
                        
                        if previous_amount > 0:
                            # Calculate profit for this sale
                            portion_sold = amount / previous_amount
                            cost_basis_portion = previous_cost * portion_sold
                            profit = value - cost_basis_portion
                            
                            # Record the trade
                            wallet_trades[from_wallet].append({
                                'date': date,
                                'type': 'sell',
                                'amount': amount,
                                'value': value,
                                'profit': profit
                            })
                            
                            # Update position
                            wallet_positions[from_wallet]['amount'] -= amount
                            wallet_positions[from_wallet]['cost_basis'] -= cost_basis_portion
                    
                    if to_wallet != 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': # Not a burn
                        # Buyer is receiving tokens
                        wallet_positions[to_wallet]['amount'] += amount
                        wallet_positions[to_wallet]['cost_basis'] += value
                        
                        # Record the trade
                        wallet_trades[to_wallet].append({
                            'date': date,
                            'type': 'buy',
                            'amount': amount,
                            'value': value
                        })
        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue
    
    # Get current token price
    current_price = get_current_token_price(token_address, api_key)
    print(f"Current estimated token price: {current_price} SOL per token")
    
    # Calculate stats for each wallet including unrealized gains
    for wallet, trades in wallet_trades.items():
        total_invested = 0
        total_returned = 0
        total_profit = 0
        
        for trade in trades:
            if trade['type'] == 'buy':
                total_invested += trade['value']
            elif trade['type'] == 'sell':
                total_returned += trade['value']
                total_profit += trade.get('profit', 0)
        
        # Get current holdings and value
        current_holdings = wallet_positions[wallet]['amount']
        current_holdings_value = current_holdings * current_price
        
        # Calculate combined value (realized profit + holdings value)
        combined_value = total_profit + current_holdings_value
        
        # Calculate ROI
        roi = 0
        if total_invested > 0:
            roi = ((total_returned + current_holdings_value - total_invested) / total_invested) * 100
        
        wallet_stats[wallet] = {
            'wallet': wallet,
            'total_invested': total_invested,
            'realized_returns': total_returned,
            'realized_profit': total_profit,
            'current_holdings': current_holdings,
            'holdings_value': current_holdings_value,
            'combined_value': combined_value,
            'roi': roi,
            'trade_count': len(trades)
        }
    
    # Sort by combined value (realized profit + holdings value)
    best_traders = sorted(wallet_stats.values(), key=lambda x: x['combined_value'], reverse=True)
    
    return best_traders

def get_current_token_price(token_address, api_key):
    """
    Estimate the current price of a token by looking at recent transactions
    
    Args:
        token_address (str): The address of the Solana token
        api_key (str): Your Helius API key
        
    Returns:
        float: Estimated current price per token
    """
    # Try to get recent transactions to estimate price
    url = f"https://api.helius.xyz/v0/addresses/{token_address}/transactions"
    params = {
        "api-key": api_key,
        "limit": 75  # Look at 20 recent transactions
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Could not fetch recent transactions for pricing")
            return 0
            
        transactions = response.json()
        if not transactions or len(transactions) == 0:
            print("No recent transactions found for pricing")
            return 0
            
        # Track all price points we find
        price_points = []
        
        # Look through recent transactions to estimate price
        for tx in transactions:
            for tokenTransfer in tx.get('tokenTransfers', []):
                if tokenTransfer.get('mint') == token_address:
                    amount = tokenTransfer.get('tokenAmount')
                    if amount <= 0:
                        continue
                        
                    # Look for corresponding SOL transfer
                    for nativeTransfer in tx.get('nativeTransfers', []):
                        value = nativeTransfer.get('amount', 0)
                        if value > 0:
                            # Found a price point
                            price_per_token = value / amount
                            price_points.append(price_per_token)
                            break
        
        # If we found at least one price point
        if price_points:
            # Use median to avoid outliers
            return sorted(price_points)[len(price_points)//2]
        
        # Alternatively, try to get price from token metadata or other sources
        return try_get_price_from_metadata(token_address, api_key)
        
    except Exception as e:
        print(f"Error getting current token price: {e}")
        return 0

def try_get_price_from_metadata(token_address, api_key):
    """
    Try to get token price from metadata or other sources
    
    Args:
        token_address (str): The token address
        api_key (str): Your Helius API key
        
    Returns:
        float: Estimated price or 0 if not found
    """
    # This is a placeholder for potential integration with price APIs
    # You could integrate with Jupiter, Raydium, or other Solana DEXes here
    print("No price data from transactions, trying Jupiter API...")
    
    # For now, we'll just look at metadata
    metadata_url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={api_key}"
    response = requests.post(metadata_url, json={"mintAccounts": [token_address]})
    
    if response.status_code == 200:
        metadata = response.json()
        if metadata and len(metadata) > 0:
            print(f"Token metadata found: {metadata[0].get('name', 'Unknown')}")
            # Some tokens include price info in metadata, but most don't
            # This is a simple placeholder
            
    # If all else fails, return a small default value
    # In a real implementation, you'd want to fetch from a DEX API
    return 0.000001  # Default tiny price if we can't determine real price

def try_alternative_endpoints(token_address, api_key):
    """
    Try alternative Helius API endpoints if the transactions endpoint fails
    
    Args:
        token_address (str): The address of the Solana token to analyze
        api_key (str): Your Helius API key
        
    Returns:
        dict: Information about the token and activity
    """
    # Try to get token metadata
    metadata_url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={api_key}"
    response = requests.post(metadata_url, json={"mintAccounts": [token_address]})
    
    if response.status_code == 200:
        metadata = response.json()
        if metadata and len(metadata) > 0:
            print(f"Token metadata found: {metadata[0].get('name', 'Unknown')}")
            return {"token_info": metadata[0]}
    
    # Try to get active wallets directly
    active_url = f"https://api.helius.xyz/v0/tokens/active-wallets?api-key={api_key}"
    response = requests.post(active_url, json={"query": {"mints": [token_address]}})
    
    if response.status_code == 200:
        active_data = response.json()
        print(f"Found {len(active_data.get('data', []))} active wallets")
        return {"active_wallets": active_data.get('data', [])}
    
    return {"error": "No alternative data found"}

def zenithfinderbot(token_addresses):
    # Replace with your actual token address and API key
    token_addresses = token_addresses
    #token_address = 'CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump'
    api_key = '9cace635-de24-4fe6-8a42-db3f605b77fc'
    
    for token_address in token_addresses:
        
        # Skip the first 100,000 transactions
        skip_count = 3000
        
        # Find the best traders after skipping transactions
        best_traders = find_best_traders(token_address, api_key, skip_transactions=skip_count)
        good_wallets = []
        
        # If no traders found, try alternative methods
        if not best_traders:
            print("\nAttempting to find alternative information about this token...")
            alt_info = try_alternative_endpoints(token_address, api_key)
            
            if "active_wallets" in alt_info and alt_info["active_wallets"]:
                wallets = alt_info["active_wallets"]
                print(f"\nTop Active Wallet Addresses:")
                for i, wallet in enumerate(wallets[:75], 1):
                    print(f"{wallet.get('wallet', 'Unknown')}")
            else:
                print("\nNo wallet addresses found")
            return
        
        # Display only wallet addresses
        print(f"\nTop Wallet Addresses:")
        for trader in best_traders[:75]:
            print(f"{trader['wallet']}")
            good_wallets.append(trader['wallet'])
            print(good_wallets)
        all_wallets.append(good_wallets)
    
    common_addresses = { "No Addresses Found": 0}

    from collections import Counter

    def count_elements(all_addresses):
        # Flatten the list of lists into a single list
        flat_list = [item for sublist in all_addresses for item in sublist]
        
        # Use Counter to count occurrences of each element
        return Counter(flat_list)

    # Example usage

    counts = count_elements(all_wallets)

    print("Element Counts:")
    for key, value in counts.items():
        if value > 1:
            common_addresses[key] = value
            return(common_addresses)
        return(common_addresses)
    
    
    

    #print(common_addresses)

#if __name__ == "__main__":
   # main()
   
#print(zenithfinderbot(['CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump','2qEHjDLDLbuBgRYvsxhc5D6uDWAivNFZGan56P1tpump']))
