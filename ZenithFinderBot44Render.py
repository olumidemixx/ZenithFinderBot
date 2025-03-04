
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive

import asyncio
from typing import List, Set, Dict
import time
from concurrent.futures import ThreadPoolExecutor
from toptradersbysellsAndUnrealizedPSKipFirst100000Orso import zenithfinderbot
from flask import Flask, request

from aiohttp import web
from pyngrok import ngrok
import logging
import sys
import os

BOT_TOKEN = '7971111200:AAFXXq0qrlA_TTaotF-aAN98YEeTr8ZMRAU'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


ELIGIBLE_USER_IDS = [6364570277, 8160840495, 987654321]
thread_pool = ThreadPoolExecutor(max_workers=10)  # Limit concurrent operations

# Flask app
app = Flask(__name__)

def check_user_eligibility(user_id: int) -> bool:
    return user_id in ELIGIBLE_USER_IDS

class UserTokenChecker:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.is_running = False
        self.addresses: Set[str] = set()
        self.task = None
        self.last_results: Dict[str, str] = {}
        self.processing = False

    async def start_checking(self):
        if not self.is_running:
            self.is_running = True
            while self.is_running:
                if self.addresses and not self.processing:
                    try:
                        self.last_results = await self.check_addresses_async(list(self.addresses))
                    except Exception as e:
                        logging.error(f"Error in zenithfinderbot for user {self.user_id}: {str(e)}")
                await asyncio.sleep(30)

    async def check_addresses_async(self, addresses: List[str]) -> Dict[str, str]:
        self.processing = True
        try:
            return await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                zenithfinderbot, 
                addresses
            )
        finally:
            self.processing = False

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
    
    checker = bot_manager.get_or_create_checker(user_id)
    if not checker.is_running:
        checker.task = asyncio.create_task(checker.start_checking())
        await update.message.reply_text("Bot started. Now monitoring addresses for your session.")
    else:
        await update.message.reply_text("Your bot session is already running.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return
    
    checker = bot_manager.get_or_create_checker(user_id)
    if checker.is_running:
        checker.stop_checking()
        bot_manager.remove_checker(user_id)
        await update.message.reply_text("Bot stopped. No longer monitoring addresses for your session.")
    else:
        await update.message.reply_text("Your bot session is not running.")

async def list_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return

    checker = bot_manager.get_or_create_checker(user_id)
    await update.message.reply_text("Getting common addresses, please wait.....")

    text = update.message.text.replace('/list', '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if not 2 <= len(addresses) <= 10:
        await update.message.reply_text("Please provide between 2 and 10 addresses.")
        return

    checker.clear_addresses()
    checker.add_addresses(addresses)

    # Create a background task for address checking
    async def check_addresses_task():
        try:
            results = await checker.check_addresses_async(addresses)
            result_message = "Here's the List of Good Addresses and the number of Common Tokens:\n\n"
            for addr, count in results.items():
                #await update.message.reply_text(f"{addr} and {count}")
                if addr or count is None:
                    pass
                    await update.message.reply_text(f"no address found", parse_mode='MarkdownV2')
                result_message += f"Address: `{addr}`\nNumber of common tokens: {count}\n\n"
            await update.message.reply_text(result_message, parse_mode='MarkdownV2')
            await update.message.reply_text("Program Completed")
        except Exception as e:
            await update.message.reply_text(f"Error checking addresses: {str(e)}")

    # Launch the task without awaiting it
    asyncio.create_task(check_addresses_task())

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return
    
    help_text = """This is all you need to know to use the bot:

There are Three commands: /start /list /help

Although /list comes in different formats e.g /list1, /list2 etc.

To use any /list format, use 2 - 10 tokens

For instance:
/list 8FqXr6dw5NHA2TtwFeDz6q9p7y9uWyoEdZmpXqqUpump, 7mHCx9iXPJ7EJDbDAUGmej39Kme8cxZfeVi1EAvEpump

Each token should be separated by a comma and a space afterwards.

I'll advise you input between 8 - 10 tokens to get the common addresses between them

You can then use tools like Gmgn website/bot, Cielo and so on to check the winrate and other qualities of these common addresses"""
    
    await update.message.reply_text(help_text)
    
    
    
    
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

application = Application.builder().token(BOT_TOKEN).build()

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("stop", stop))
application.add_handler(CommandHandler("list", list_addresses))
application.add_handler(CommandHandler("help", help))

def initialize_bot():
    """Initialize the bot"""
    global bot_initialized
    if bot_initialized:
        return True
        
    try:
        # Create an event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize the application
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.start())
        
        # Set webhook URL
        webhook_url = os.environ.get("RENDER_EXTERNAL_URL", "https://zenithfinderbot.onrender.com")
        success = loop.run_until_complete(setup_webhook(webhook_url))
        
        if success:
            bot_initialized = True
            logger.info("Bot initialized successfully")
            return True
        else:
            logger.error("Failed to set webhook")
            return False
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")
        return False

# Webhook route for Telegram
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram"""
    if request.method == "POST":
        try:
            # Make sure bot is initialized
            if not bot_initialized and not initialize_bot():
                return 'Bot initialization failed', 500
            
            # Create an asyncio event loop for handling the update
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Process the update
            update = Update.de_json(request.get_json(force=True), application.bot)
            loop.run_until_complete(application.process_update(update))
            
            return 'ok'
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")
            return str(e), 500
    return 'ok'

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    # Initialize bot if not already initialized
    if not bot_initialized:
        if initialize_bot():
            return 'Bot initialized and running!', 200
        else:
            return 'Bot initialization failed', 500
    return 'Bot is running!', 200

# Ping endpoint to keep the service alive
@app.route('/ping', methods=['GET'])
def ping():
    """Ping endpoint to prevent Render from sleeping"""
    # Initialize bot if not already initialized
    if not bot_initialized:
        initialize_bot()
    return 'Pong!', 200

# Root endpoint
@app.route('/', methods=['GET'])
def index():
    """Root endpoint for checking if server is running"""
    return 'ZenithFinder Bot is running. Set your webhook to receive updates.', 200

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8443))
    
    # Initialize bot on startup
    initialize_bot()
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=port)
