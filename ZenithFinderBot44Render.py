import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import asyncio
from typing import List, Set, Dict
import time
from concurrent.futures import ThreadPoolExecutor
#from toptradersbysellsAndUnrealizedPSKipFirst100000Orso import topTraders,earlyBuyers,topHolders,single_topTraders,single_topHolders
from traders import topTraders
from holders import topHolders
from earlyBuyers import earlyBuyers
from single_traders import single_topTraders
from single_holders import single_topHolders
from aiohttp import web
from pyngrok import ngrok
import logging
import re
import sys
import os



from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

BOT_TOKEN = os.getenv('BOT_TOKEN')


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ELIGIBLE_USER_IDS = [6364570277, 8160840495, 7172794326, 5825587838, 1786613658, 6058881388]
thread_pool = ThreadPoolExecutor(max_workers=10)  # Limit concurrent operations
# Add this at the top level of your module, with your other imports
get_results = ""  # Initialize with empty string

def check_user_eligibility(user_id: int) -> bool:
    return user_id in ELIGIBLE_USER_IDS

class UserTokenChecker:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.is_running = False
        self.addresses: Set[str] = set()
        self.task = None
        self.last_results: Dict[str, str] = {}
        self.active_requests = 0  # Track active requests per user instead of a simple flag

    async def start_checking(self):
        if not self.is_running:
            self.is_running = True
            while self.is_running:
                if self.addresses and self.active_requests == 0:  # Only auto-check when no manual checks are running
                    try:
                        self.last_results = await self.check_addresses_async(list(self.addresses))
                    except Exception as e:
                        logging.error(f"Error in topTraders for user {self.user_id}: {str(e)}")
                await asyncio.sleep(30)

    async def check_addresses_async(self, addresses: List[str]) -> Dict[str, str]:
        self.active_requests += 1  # Increment active request counter
        try:
            return await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                topTraders, 
                addresses
            )
        finally:
            self.active_requests -= 1  # Decrement when done

    async def check_addresses_async_th(self, addresses: List[str]) -> Dict[str, str]:
        self.active_requests += 1  # Increment active request counter
        try:
            return await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                topHolders, 
                addresses
            )
        finally:
            self.active_requests -= 1  # Decrement when done


    async def check_addresses_async_stt(self, addresses: List[str]) -> Dict[str, str]:
        self.active_requests += 1  # Increment active request counter
        try:
            return await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                single_topTraders, 
                addresses
            )
        finally:
            self.active_requests -= 1  # Decrement when done
            
    
    async def check_addresses_async_sth(self, addresses: List[str]) -> Dict[str, str]:
        self.active_requests += 1  # Increment active request counter
        try:
            return await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                single_topHolders, 
                addresses
            )
        finally:
            self.active_requests -= 1  # Decrement when done




    async def check_addresses_async_ea(self, addresses: List[str]) -> Dict[str, str]:
        self.active_requests += 1  # Increment active request counter
        try:
            return await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                earlyBuyers, 
                addresses
            )
        finally:
            self.active_requests -= 1  # Decrement when done

    def stop_checking(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            self.task = None

    def add_addresses(self, new_addresses: List[str]):
        self.addresses.update(new_addresses)

    def clear_addresses(self):
        self.addresses.clear()
        self.last_results.clear()

    def get_latest_results(self) -> Dict[str, str]:
        return self.last_results

class BotManager:
    def __init__(self):
        self.user_checkers: Dict[int, UserTokenChecker] = {}

    def get_or_create_checker(self, user_id: int) -> UserTokenChecker:
        if user_id not in self.user_checkers:
            self.user_checkers[user_id] = UserTokenChecker(user_id)
        return self.user_checkers[user_id]

    def remove_checker(self, user_id: int):
        if user_id in self.user_checkers:
            checker = self.user_checkers[user_id]
            checker.stop_checking()
            del self.user_checkers[user_id]

# Initialize the bot manager
bot_manager = BotManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return
    await update.message.reply_text("Welcome, Try the /tt or /th command 2 more times if you do not get an address as an output\nIf you do not get any wallets still, then there are no outputs\nIf not, you get your wallets\n\nUse the /help command to learn how to use me.  ")
    
    
    checker = bot_manager.get_or_create_checker(user_id)
    if not checker.is_running:
        checker.task = asyncio.create_task(checker.start_checking())
        await update.message.reply_text("Join t.me/Smart_Money_Buy to get alpha calls by Zenith Bot")
    else:
        await update.message.reply_text("Your bot session is already running.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.\n contact @thegroovymate to test it out")
        return
    
    checker = bot_manager.get_or_create_checker(user_id)
    if checker.is_running:
        checker.stop_checking()
        bot_manager.remove_checker(user_id)
        await update.message.reply_text("Bot stopped. No longer monitoring addresses for your session.")
    else:
        await update.message.reply_text("Your bot session is not running.")

async def process_list_command(update: Update, addresses: List[str]):
    """Process a single list command independent of other users' commands"""
    user_id = update.effective_user.id
    checker = bot_manager.get_or_create_checker(user_id)
    
    try:
        await update.message.reply_text("Processing addresses, please wait...")
        results = await checker.check_addresses_async(addresses)
        logging.info(results)
        
        if results is None or not results:
            await update.message.reply_text("No common addresses found between these tokens.")
            return
            
        result_message = "Here's the List of Good Addresses and the number of Common Tokens:\n\n"
        for addr, count in results.items():
            if addr and count is not None:
                result_message += f"Address: `{addr}`\nNumber of common tokens: {count}\n\n"
        
        await update.message.reply_text(result_message, parse_mode='MarkdownV2')
        await update.message.reply_text("Command completed successfully")
        global get_results
        get_results = result_message
    except Exception as e:
        logging.error(f"Error processing list command for user {user_id}: {str(e)}")
        await update.message.reply_text(f"Error checking addresses: {str(e)}")


async def process_list_command_th(update: Update, addresses: List[str]):
    """Process a single list command independent of other users' commands"""
    user_id = update.effective_user.id
    checker = bot_manager.get_or_create_checker(user_id)
    
    try:
        await update.message.reply_text("Processing addresses, please wait...")
        results = await checker.check_addresses_async_th(addresses)
        
        if results is None or not results:
            await update.message.reply_text("No common addresses found between these tokens.")
            return
            
        result_message = "Here's the List of Good Addresses and the number of Common Tokens:\n\n"
        for addr, count in results.items():
            if addr and count is not None:
                result_message += f"Address: `{addr}`\nNumber of common tokens: {count}\n\n"
        
        await update.message.reply_text(result_message, parse_mode='MarkdownV2')
        await update.message.reply_text("Command completed successfully")
        global get_results
        get_results = result_message
    except Exception as e:
        logging.error(f"Error processing list command for user {user_id}: {str(e)}")
        await update.message.reply_text(f"Error checking addresses: {str(e)}")
        
        
        
async def process_list_command_stt(update: Update, addresses: List[str]):
    """Process a single list command independent of other users' commands"""
    user_id = update.effective_user.id
    checker = bot_manager.get_or_create_checker(user_id)
    
    try:
        await update.message.reply_text("Processing addresses, please wait...")
        results = await checker.check_addresses_async_stt(addresses)
        
        if results is None or not results:
            await update.message.reply_text("No common addresses found between these tokens.")
            return
            
        result_message = "Here's the Top 40 Top Traders:\n\n"
        for addr, count in results.items():
            if addr and count is not None:
                result_message += f"`{addr}`\n"
        
        await update.message.reply_text(result_message, parse_mode='MarkdownV2')
        await update.message.reply_text("Command completed successfully")
        global get_results
        get_results = result_message
    except Exception as e:
        logging.error(f"Error processing list command for user {user_id}: {str(e)}")
        await update.message.reply_text(f"Error checking addresses: {str(e)}")
        
        
        
async def process_list_command_sth(update: Update, addresses: List[str]):
    """Process a single list command independent of other users' commands"""
    user_id = update.effective_user.id
    checker = bot_manager.get_or_create_checker(user_id)
    
    try:
        await update.message.reply_text("Processing addresses, please wait...")
        results = await checker.check_addresses_async_sth(addresses)
        
        if results is None or not results:
            await update.message.reply_text("No common addresses found between these tokens.")
            return
            
        result_message = "Here's the Top 40 Top Holders:\n\n"
        for addr, count in results.items():
            if addr and count is not None:
                result_message += f"`{addr}`\n"
        
        await update.message.reply_text(result_message, parse_mode='MarkdownV2')
        await update.message.reply_text("Command completed successfully")
        global get_results
        get_results = result_message
    except Exception as e:
        logging.error(f"Error processing list command for user {user_id}: {str(e)}")
        await update.message.reply_text(f"Error checking addresses: {str(e)}")





async def process_list_command_ea(update: Update, addresses: List[str]):
    """Process a single list command independent of other users' commands"""
    user_id = update.effective_user.id
    checker = bot_manager.get_or_create_checker(user_id)
    
    try:
        await update.message.reply_text("Processing addresses, please wait...")
        results = await checker.check_addresses_async_ea(addresses)
        
        if results is None or not results:
            await update.message.reply_text("No common addresses found between these tokens.")
            return
            
        result_message = "Here's the List of Good Addresses and the number of Common Tokens:\n\n"
        for addr, count in results.items():
            if addr and count is not None:
                result_message += f"Address: `{addr}`\nNumber of common tokens: {count}\n\n"
        
        await update.message.reply_text(result_message, parse_mode='MarkdownV2')
        await update.message.reply_text("Command completed successfully")
        global get_results
        get_results = result_message
    except Exception as e:
        logging.error(f"Error processing list command for user {user_id}: {str(e)}")
        await update.message.reply_text(f"Error checking addresses: {str(e)}")



async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return

    # Extract command name to handle different list variants
    command = update.message.text.split()[0].lower()
    list_variant = command.replace('/tt', '')  # Will be empty for /list or have a number for /list1, /list2, etc.
    
    text = update.message.text.replace(command, '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if not 2 <= len(addresses) <= 10:
        await update.message.reply_text("Please provide between 2 and 10 addresses.")
        return

    # Create a new task for this specific request
    # This allows multiple requests to run concurrently
    asyncio.create_task(process_list_command(update, addresses))
    await update.message.reply_text("Use @GMGN_smartmoney_bot or Cielo to filter the wallets based on winrate and Pnls")

    
    # Optional: you can track which variant was used if needed
    logging.info(f"User {user_id} used list variant: {list_variant or 'default'}")
    

async def stt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return

    # Extract command name to handle different list variants
    command = update.message.text.split()[0].lower()
    list_variant = command.replace('/stt', '')  # Will be empty for /list or have a number for /list1, /list2, etc.
    
    text = update.message.text.replace(command, '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if len(addresses) != 1:
        await update.message.reply_text("Please provide only  1 address.")
        return

    # Create a new task for this specific request
    # This allows multiple requests to run concurrently
    asyncio.create_task(process_list_command_stt(update, addresses))
    
    # Optional: you can track which variant was used if needed
    logging.info(f"User {user_id} used list variant: {list_variant or 'default'}")
    
    
async def get_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global get_results
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return
    one = r'[0-9A-HJ-NP-Za-km-z]{32,44}'
    twi = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
    combined_pattern = r'[0-9A-HJ-NP-Za-km-z]{32,44}|\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
    all_addresses = re.findall(combined_pattern, get_results)
    send = ""
    for address in all_addresses:
        send += address + "\n"
    await update.message.reply_text(send)




async def th(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return

    # Extract command name to handle different list variants
    command = update.message.text.split()[0].lower()
    list_variant = command.replace('/th', '')  # Will be empty for /list or have a number for /list1, /list2, etc.
    
    text = update.message.text.replace(command, '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if not 2 <= len(addresses) <= 10:
        await update.message.reply_text("Please provide between 2 and 10 addresses.")
        return

    # Create a new task for this specific request
    # This allows multiple requests to run concurrently
    asyncio.create_task(process_list_command_th(update, addresses))
    await update.message.reply_text("Use @GMGN_smartmoney_bot or Cielo to filter the wallets based on winrate and Pnls")

    
    

async def sth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return

    # Extract command name to handle different list variants
    command = update.message.text.split()[0].lower()
    list_variant = command.replace('/sth', '')  # Will be empty for /list or have a number for /list1, /list2, etc.
    
    text = update.message.text.replace(command, '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if  len(addresses) !=  1:
        await update.message.reply_text("Please provide only 1 address.")
        return

    # Create a new task for this specific request
    # This allows multiple requests to run concurrently
    asyncio.create_task(process_list_command_sth(update, addresses))




async def ea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return

    # Extract command name to handle different list variants
    command = update.message.text.split()[0].lower()
    list_variant = command.replace('/ea', '')  # Will be empty for /list or have a number for /list1, /list2, etc.
    
    text = update.message.text.replace(command, '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if not 2 <= len(addresses) <= 10:
        await update.message.reply_text("Please provide between 2 and 10 addresses.")
        return

    # Create a new task for this specific request
    # This allows multiple requests to run concurrently
    asyncio.create_task(process_list_command_ea(update, addresses))

    
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return
    
    help_text = """This is all you need to know to use the bot:

There are 6 commands: /start /th /tt /sth /stt /help



To use the /tt and /th  format, use 2 - 10 tokens

For instance:
/tt 8FqXr6dw5NHA2TtwFeDz6q9p7y9uWyoEdZmpXqqUpump, 7mHCx9iXPJ7EJDbDAUGmej39Kme8cxZfeVi1EAvEpump

/tt is great for finding smart traders and insiders
/th is great for finding smart whales

I'll advise you input between 4 - 5 tokens to get the common addresses between them

To use the /stt and /sth  format, use 1 token

For instance:
/stt 8FqXr6dw5NHA2TtwFeDz6q9p7y9uWyoEdZmpXqqUpump

/stt is great for finding the top 40 smart traders of a token
/sth is great for finding the top 40 smart holders of a token

Each token should be separated by a comma and a space afterwards.

You can then use tools like Gmgn website/bot, Cielo and so on to check the winrate and other qualities of these common addresses

Contact @TheGroovyMate to test the Vip bot  and follow him on Twitter at: https://x.com/Groovy_mate
"""
    
    await update.message.reply_text(help_text)
    
# Home page handler
async def home_page(request):
    """Handle requests to the home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Zenith Finder Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                text-align: center;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 600px;
                margin: 50px auto;
                padding: 30px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4CAF50;
            }
            p {
                font-size: 18px;
                line-height: 1.6;
            }
            .status {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Zenith Finder Bot</h1>
            <p>This bot helps you find common addresses between tokens.</p>
            <div class="status">Bot is running ✓</div>
            <p>Use Telegram to interact with the bot.</p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')
    
from aiohttp import web
from pyngrok import ngrok
import logging
import sys
import asyncio

async def setup_webhook(application: Application, webhook_url: str):
    """Setup webhook for the bot"""
    webhook_path = f"/{BOT_TOKEN}"
    await application.bot.set_webhook(url=webhook_url + webhook_path)
    return webhook_path

async def handle_webhook(request):
    """Handle incoming webhook requests"""
    try:
        update = Update.de_json(await request.json(), application.bot)
        await application.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        logging.error(f"Error processing update: {e}")
        return web.Response(status=500)

async def on_startup(web_app):
    """Setup webhook on startup"""
    global application
    
    try:
        # Initialize the application
        await application.initialize()
        await application.start()
        
        # Use Render URL from environment variable
        webhook_url = "https://zenithfinderbot.onrender.com"
        if not webhook_url:
            logging.error("RENDER_EXTERNAL_URL environment variable not found")
            await application.shutdown()
            sys.exit(1)
            
        logging.info(f"Using Render URL: {webhook_url}")
        
        # Setup webhook
        webhook_path = await setup_webhook(application, webhook_url)
        
        # Add webhook handler
        web_app.router.add_post(webhook_path, handle_webhook)
        
    except Exception as e:
        logging.error(f"Startup failed: {e}")
        await application.shutdown()
        sys.exit(1)

async def on_shutdown(web_app):
    logging.info("yeahhhhh")
    """Cleanup on shutdown"""
    #global application
    #await application.bot.delete_webhook()
    #await application.stop()
    #await application.shutdown()


def main():
    
    global application
    
    # Initialize the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler(["tt", "tt1", "tt2", "tt3", "tt4", "tt5"], tt))
    application.add_handler(CommandHandler(["th", "th1", "th2", "th3", "th4", "th5"], th))
    application.add_handler(CommandHandler(["stt", "stt1", "stt2", "stt3", "stt4", "stt5"], stt))
    application.add_handler(CommandHandler(["sth", "sth1", "sth2", "sth3", "sth4", "sth5"], sth))
    application.add_handler(CommandHandler(["ea", "ea1", "ea2", "ea3", "ea4", "ea5"], ea))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("get_result", get_result))

    # Setup web application
    web_app = web.Application()
    web_app.on_startup.append(on_startup)
    web_app.on_shutdown.append(on_shutdown)
    
    # Add home page route
    web_app.router.add_get('/', home_page)

    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8443))
    
    # Start the web server
    # When running on Render, we need to bind to 0.0.0.0 instead of localhost
    host = '0.0.0.0' if os.environ.get("RENDER_EXTERNAL_URL") else 'localhost'
    web.run_app(web_app, host=host, port=port)

if __name__ == '__main__':
    main()
