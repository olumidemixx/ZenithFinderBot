import requests
import json
from datetime import datetime
from collections import defaultdict, Counter
import time

all_wallets = []

def find_best_traders(token_address, api_key, limit=100, skip_transactions=1, max_pages=50):
    """
    Find the best traders for a specific Solana token using Helius API,
    focusing only on selling activity
    
    Args:
        token_address (str): The address of the Solana token to analyze
        api_key (str): Your Helius API key
        limit (int): Number of transactions to fetch per page
        skip_transactions (int): Number of transactions to skip before analyzing
        max_pages (int): Maximum number of pages to fetch after skipping
        
    Returns:
        list: Sorted list of traders by sell profits only
    """
    # Helius API endpoint
    url = f"https://api.helius.xyz/v0/addresses/{token_address}/transactions"
    
    # Parameters for the API request
    params = {
        "api-key": api_key,
        "limit": limit
    }
    
    # Skip to desired transaction position
    before_param = None
    
    # Calculate how many pages to skip
    pages_to_skip = skip_transactions // limit
    remaining_to_skip = skip_transactions % limit
    
    # First, navigate to the approximate position by skipping full pages
    for page in range(pages_to_skip):
        if before_param:
            params["before"] = before_param
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return []
        
        transactions = response.json()
        
        # Check if we hit the end
        if not transactions or len(transactions) == 0:
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
            return []
            
        transactions = response.json()
        
        if not transactions or len(transactions) == 0:
            return []
            
        # Get the signature of the last transaction at our desired starting point
        start_index = remaining_to_skip
        if len(transactions) > start_index:
            before_param = transactions[start_index].get('signature')
        else:
            before_param = transactions[-1].get('signature')
            
        time.sleep(0.5)
    
    # Now continue with collecting the transactions we want to analyze
    all_transactions = []
    
    for page in range(max_pages):
        if before_param:
            params["before"] = before_param
            
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            if page == 0:
                return []
            break
        
        transactions = response.json()
        
        if isinstance(transactions, dict) and "error" in transactions:
            if page == 0:
                return []
            break
            
        if not transactions or len(transactions) == 0:
            break
            
        all_transactions.extend(transactions)
        
        if len(transactions) > 0:
            last_tx = transactions[-1]
            before_param = last_tx.get('signature')
        else:
            break
            
        time.sleep(0.5)
    
    if len(all_transactions) == 0:
        return []
    
    # Track wallet positions for cost basis calculation
    wallet_positions = defaultdict(lambda: {'amount': 0, 'cost_basis': 0})
    
    # Track only selling activity per wallet
    wallet_sells = defaultdict(lambda: {'total_profit': 0, 'sell_count': 0, 'total_sell_value': 0})
    
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
                    
                    # Track buy transactions ONLY to calculate cost basis
                    if to_wallet != 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': # Not a burn
                        # Buyer is receiving tokens - update position for future sell profit calculation
                        wallet_positions[to_wallet]['amount'] += amount
                        wallet_positions[to_wallet]['cost_basis'] += value
                    
                    # Track ONLY sell transactions for ranking
                    if from_wallet != 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': # Not a mint
                        # Seller is sending tokens out
                        previous_amount = wallet_positions[from_wallet]['amount']
                        previous_cost = wallet_positions[from_wallet]['cost_basis']
                        
                        if previous_amount > 0:
                            # Calculate profit for this sale
                            portion_sold = amount / previous_amount
                            cost_basis_portion = previous_cost * portion_sold
                            profit = value - cost_basis_portion
                            
                            # Record the sell activity
                            wallet_sells[from_wallet]['total_profit'] += profit
                            wallet_sells[from_wallet]['sell_count'] += 1
                            wallet_sells[from_wallet]['total_sell_value'] += value
                            
                            # Update position
                            wallet_positions[from_wallet]['amount'] -= amount
                            wallet_positions[from_wallet]['cost_basis'] -= cost_basis_portion
        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue
    
    # Create stats for each wallet based ONLY on selling activity
    wallet_stats = {}
    
    for wallet, sell_data in wallet_sells.items():
        # Only include wallets that have actually sold tokens
        if sell_data['sell_count'] > 0:
            wallet_stats[wallet] = {
                'wallet': wallet,
                'total_sell_profit': sell_data['total_profit'],
                'sell_count': sell_data['sell_count'],
                'total_sell_value': sell_data['total_sell_value'],
                # We could add average profit per sell if needed
                'avg_profit_per_sell': sell_data['total_profit'] / sell_data['sell_count'] if sell_data['sell_count'] > 0 else 0
            }
    
    # Sort by total sell profit - focusing ONLY on selling activity
    best_sellers = sorted(wallet_stats.values(), key=lambda x: x['total_sell_profit'], reverse=True)
    
    return best_sellers

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
        "limit": 75  # Look at recent transactions
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return 0
            
        transactions = response.json()
        if not transactions or len(transactions) == 0:
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
    # Try to get token metadata
    metadata_url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={api_key}"
    response = requests.post(metadata_url, json={"mintAccounts": [token_address]})
    
    if response.status_code == 200:
        metadata = response.json()
        if metadata and len(metadata) > 0:
            pass
    
    # Default tiny price if we can't determine real price
    return 0.000001

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
            return {"token_info": metadata[0]}
    
    # Try to get active wallets directly
    active_url = f"https://api.helius.xyz/v0/tokens/active-wallets?api-key={api_key}"
    response = requests.post(active_url, json={"query": {"mints": [token_address]}})
    time.sleep(3)
    
    if response.status_code == 200:
        active_data = response.json()
        return {"active_wallets": active_data.get('data', [])}
    
    return {"error": "No alternative data found"}

def zenithfinderbot(token_addresses):
    # API key
    api_key = '939594ba-3f6d-4c8d-bd74-b13abd0bc4a9'
    
    # Clear previous results
    all_wallets.clear()
    
    for token_address in token_addresses:
        time.sleep(5)
        
        # Skip the first transaction
        skip_count = 1
        
        # Find the best traders after skipping transactions
        best_traders = find_best_traders(token_address, api_key, skip_transactions=skip_count)
        good_wallets = []
        
        # If no traders found, try alternative methods
        if not best_traders:
            alt_info = try_alternative_endpoints(token_address, api_key)
            
            if "active_wallets" in alt_info and alt_info["active_wallets"]:
                wallets = alt_info["active_wallets"]
            return {}
        
        # Collect only wallets that have made profitable sells
        for trader in best_traders:
            good_wallets.append(trader['wallet'])
        
        all_wallets.append(good_wallets)
    
    # Find common addresses across tokens
    common_addresses = {"No Addresses Found": 0}

    # Count occurrences of each wallet across all tokens
    flat_list = [item for sublist in all_wallets for item in sublist]
    
    if flat_list:
        counts = Counter(flat_list)
        
        # Filter for wallets that appear in multiple token lists
        common_addresses = {key: value for key, value in counts.items() if value > 1}
        
        # If no common addresses found, keep the default
        if not common_addresses:
            common_addresses = {"No Addresses Found": 0}
    
    print(common_addresses)
    return common_addresses
