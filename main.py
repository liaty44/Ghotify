import os
import asyncio
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Load Environment
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_CONNECTION") or os.getenv("MONGO_URI")

# Intents Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# Database Injector
async def init_db():
    if MONGO_URI:
        try:
            bot.db_client = AsyncIOMotorClient(MONGO_URI)
            bot.db = bot.db_client["Ghotify"]
            print("INFO: MongoDB cluster connected successfully!")
        except Exception as e:
            print(f"CRITICAL: MongoDB connection crash: {e}")
    else:
        print("WARNING: Database URI is missing. Stats & logs won't work.")

# Render Light Health Server (Port 10000 Fix)
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Ghotify Falcon Engine Up")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    print(f"INFO: Keep-alive server running on port {port}")
    server.serve_forever()

# Dynamic Cog Loader (Automatic Folders Scan)
async def load_extensions():
    # Scanning source categories
    base_dirs = ["src/commands", "src/events"]
    for base in base_dirs:
        if not os.path.exists(base):
            continue
        for root, _, files in os.walk(base):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    # Converting file path to python dot notation
                    relative_path = os.path.relpath(os.path.join(root, file))
                    cog_path = relative_path.replace(os.sep, ".").removesuffix(".py")
                    try:
                        await bot.load_extension(cog_path)
                        print(f"SUCCESS: Loaded module -> {cog_path}")
                    except Exception as e:
                        print(f"FAILED: Could not load module {cog_path}. Error: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Bot Engine Online: Logged in as {bot.user}")

async def main():
    # Parallel Initialization
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    await init_db()
    await load_extensions()
    
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
        
