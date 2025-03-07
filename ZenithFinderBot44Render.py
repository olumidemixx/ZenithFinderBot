import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive

import asyncio
from typing import List, Set, Dict, Optional
import time
from concurrent.futures import ThreadPoolExecutor
from toptradersbysellsAndUnrealizedPSKipFirst100000Orso import zenithfinderbot

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

ELIGIBLE_USER_IDS = [6364570277, 8160840495, 987654321]
thread_pool = ThreadPoolExecutor(max_workers=10)  # Limit concurrent operations

def check_user_eligibility(user_id: int) -> bool:
    return user_id in ELIGIBLE_USER_IDS

class UserSession:
    """Represents a single user's session with addresses to monitor"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.addresses: Set[str] = set()
        self.results: Dict[str, str] = {}

class UserTokenChecker:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.is_running = False
        self.sessions: Dict[str, UserSession] = {}  # Track multiple sessions per user
        self.task: Optional[asyncio.Task] = None
        self.processing = False
        self.current_session_id: Optional[str] = None

    async def start_checking(self):
        if not self.is_running:
            self.is_running = True
            try:
                while self.is_running:
                    # Check all sessions for this user
                    for session_id, session in list(self.sessions.items()):
                        if session.addresses and not self.processing:
                            try:
                                self.current_session_id = session_id
                                session.results = await self.check_addresses_async(list(session.addresses))
                                self.current_session_id = None
                            except Exception as e:
                                logging.error(f"Error in zenithfinderbot for user {self.user_id}, session {session_id}: {str(e)}")
                    await asyncio.sleep(30)
            except asyncio.CancelledError:
                logging.info(f"Task for user {self.user_id} was cancelled")
            except Exception as e:
                logging.error(f"Unexpected error in task for user {self.user_id}: {str(e)}")
            finally:
                self.is_running = False

    async def check_addresses_async(self, addresses: List[str]) -> Dict[str, str]:
        self.processing = True
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                thread_pool, 
                zenithfinderbot, 
                addresses
            )
            return result if result is not None else {}
        finally:
            self.processing = False

    def stop_checking(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            self.task = None

    def create_session(self) -> str:
        """Create a new session for this user and return its ID"""
        session_id = f"session_{len(self.sessions) + 1}_{int(time.time())}"
        self.sessions[session_id] = UserSession(self.user_id)
        return session_id

    def add_addresses_to_session(self, session_id: str, new_addresses: List[str]):
        """Add addresses to a specific session"""
        if session_id in self.sessions:
            self.sessions[session_id].addresses.update(new_addresses)

    def clear_session(self, session_id: str):
        """Clear addresses and results for a specific session"""
        if session_id in self.sessions:
            self.sessions[session_id].addresses.clear()
            self.sessions[session_id].results.clear()

    def get_session_results(self, session_id: str) -> Dict[str, str]:
        """Get results for a specific session"""
        if session_id in self.sessions:
            return self.sessions[session_id].results
        return {}

class BotManager:
    def __init__(self):
        self.user_checkers: Dict[int, UserTokenChecker] = {}
        # Track which session is currently being used by a user command
        self.user_active_sessions: Dict[int, str] = {}

    def get_or_create_checker(self, user_id: int) -> UserTokenChecker:
        if user_id not in self.user_checkers:
            self.user_checkers[user_id] = UserTokenChecker(user_id)
        return self.user_checkers[user_id]

    def create_session_for_user(self, user_id: int) -> str:
        """Create a new session for a user and set it as active"""
        checker = self.get_or_create_checker(user_id)
        session_id = checker.create_session()
        self.user_active_sessions[user_id] = session_id
        return session_id

    def get_active_session(self, user_id: int) -> Optional[str]:
        """Get the currently active session ID for a user"""
        return self.user_active_sessions.get(user_id)

    def remove_checker(self, user_id: int):
        if user_id in self.user_checkers:
            checker = self.user_checkers[user_id]
            checker.stop_checking()
            del self.user_checkers[user_id]
        if user_id in self.user_active_sessions:
            del self.user_active_sessions[user_id]

# Initialize the bot manager
bot_manager = BotManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_user_eligibility(user_id):
        await update.message.reply_text("Sorry, you are not eligible to use this bot.")
        return
    
    checker = bot_manager.get_or_create_checker(user_id)
    # Create an initial session
    session_id = bot_manager.create_session_for_user(user_id)
    
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
    
    # Create a new session for this list command
    session_id = bot_manager.create_session_for_user(user_id)
    
    await update.message.reply_text("Getting common addresses, please wait.....")

    text = update.message.text.replace('/list', '').strip()
    addresses = [addr.strip() for addr in text.split(',') if addr.strip()]

    if not 2 <= len(addresses) <= 10:
        await update.message.reply_text("Please provide between 2 and 10 addresses.")
        return

    # Clear and add addresses to the new session
    checker.clear_session(session_id)
    checker.add_addresses_to_session(session_id, addresses)

    # Create a background task for address checking
    async def check_addresses_task():
        try:
            results = await checker.check_addresses_async(addresses)
            if results is None:
                await update.message.reply_text("No results returned from check_addresses_async")
                return
            
            # Save results to session
            if session_id in checker.sessions:
                checker.sessions[session_id].results = results
            
            result_message = "Here's the List of Good Addresses and the number of Common Tokens:\n\n"
            for addr, count in results.items():
                if addr is None or count is None:
                    continue
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
    logging.info("Shutting down application")
    """Cleanup on shutdown"""
    #global application
    #await application.bot.delete_webhook()
    #await application.stop()
    #await application.shutdown()

keep_alive()
def main():
    
    global application
    
    # Initialize the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("list", list_addresses))
    application.add_handler(CommandHandler("help", help))

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
