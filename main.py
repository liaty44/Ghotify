import discord
from discord.ext import commands
import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from config import Config
from database import db

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger("GHOTIFY")

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.invites = True
intents.reactions = True
intents.voice_states = True

# --- RENDER PORT LISTENERS DUMMY SERVER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        return  # Terminal mein फालतू logs rokne ke liye

def run_health_server():
    # Render automatically PORT environment variable deta hai, nahi toh .env wala 8080 use hoga
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Render health check server started on port {port}")
    server.serve_forever()
# ------------------------------------------

class GhotifyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=Config.PREFIX, intents=intents, help_command=None)

    async def setup_hook(self):
        db.connect()

        if not os.path.exists('cogs'):
            os.makedirs('cogs')

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Loaded feature: {filename[:-3]}")

        await self.tree.sync()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'{Config.BOT_NAME} is officially online!')
        await self.change_presence(activity=discord.Game(name=f"{Config.PREFIX}help | @{Config.BOT_NAME}"))

bot = GhotifyBot()

if __name__ == "__main__":
    if not Config.TOKEN:
        logger.critical("BOT_TOKEN variable is missing inside the .env file!")
    else:
        # Render ke port wale system ko background thread mein chalu karna
        server_thread = threading.Thread(target=run_health_server, daemon=True)
        server_thread.start()
        
        # Bot ko run karna
        bot.run(Config.TOKEN)
