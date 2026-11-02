import os
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# 1. Load Environment Variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_CONNECTION") or os.getenv("MONGO_URI")

if not TOKEN:
    print("CRITICAL: BOT_TOKEN is missing in environment variables!")
    exit(1)

# 2. Setup Discord Intents (Instant Commands Response ke liye)
intents = discord.Intents.default()
intents.message_content = True  # Prefix commands read karne ke liye mandatory hai
intents.members = True          # Server members track karne ke liye

# Bot setup with prefix '!' (Aap ise change kar sakte hain)
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# 3. MongoDB Database Connection (Async & Fast)
db = None
if MONGO_URI:
    try:
        cluster = AsyncIOMotorClient(MONGO_URI)
        db = cluster["Ghotify"]  # Database Name
        print("INFO: MongoDB successfully connected!")
    except Exception as e:
        print(f"CRITICAL: Database connection failed: {e}")
else:
    print("WARNING: No MONGO_CONNECTION defined. Database features won't work.")

# 4. Lightweight Web Server (UptimeRobot / Cron-Job.org ko 24/7 UP rakhne ke liye)
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"GHOTIFY IS ALIVE")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))  # Render default port 10000 use karega
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    print(f"INFO: Render health check server started on port {port}")
    server.serve_forever()

# 5. Bot Events
@bot.event
async def on_ready():
    print(f"INFO: Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("INFO: GHOTIFY is officially online and ready to respond instant!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    # Agar bot ko tag/ping kiya jaye toh instant reply
    if bot.user.mentioned_in(message) and len(message.content.split()) == 1:
        await message.channel.send(f"Hey! My prefix is `!`. Type `!help` to see all commands.")
        return

    # Yeh line prefix commands ko execute karne ke liye sabse zaroori hai
    await bot.process_commands(message)

# 6. Sample Instant Commands
@bot.command()
async def ping(ctx):
    """Bot latency check karne ke liye instant command"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency is `{latency}ms`")

@bot.command()
async def help(ctx):
    """Custom Help Menu"""
    embed = discord.Embed(title="Ghostify Bot Commands", color=discord.Color.red())
    embed.add_field(name="⚙️ Utility", value="`!ping` - Check latency\n`!uptime` - Check bot status", inline=False)
    embed.add_field(name="🛡️ Moderation", value="`!kick @user` - Kick member\n`!ban @user` - Ban member", inline=False)
    embed.set_footer(text="Ghotify Falcon • Instant Response Mode")
    await ctx.send(embed=embed)

@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="No reason provided"):
    """Instant Member Kick Command"""
    if not ctx.author.guild_permissions.kick_members:
        return await ctx.send("❌ Aapke paas `Kick Members` ki permission nahi hai.")
    if not member:
        return await ctx.send("❌ Please mention a user to kick. Example: `!kick @username`")
    
    await member.kick(reason=reason)
    await ctx.send(f"✅ **{member.name}** ko successfully kick kar diya gaya hai. Reason: {reason}")

@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="No reason provided"):
    """Instant Member Ban Command"""
    if not ctx.author.guild_permissions.ban_members:
        return await ctx.send("❌ Aapke paas `Ban Members` ki permission nahi hai.")
    if not member:
        return await ctx.send("❌ Please mention a user to ban. Example: `!ban @username`")
    
    await member.ban(reason=reason)
    await ctx.send(f"✅ **{member.name}** ko successfully ban kar diya gaya hai. Reason: {reason}")

# 7. Start the Web Server & Bot
if __name__ == "__main__":
    # Web server ko alag thread me chalana taaki bot block na ho
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Start bot
    bot.run(TOKEN)
    
