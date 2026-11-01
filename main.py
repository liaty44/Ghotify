import discord
from discord.ext import commands
import os
import asyncio
import logging
from config import Config
from database import db

# Logging setup takki errors terminal me dikhein
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger("GHOTIFY")

# Discord Intents Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.invites = True
intents.reactions = True
intents.voice_states = True

class GhotifyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=Config.PREFIX, intents=intents, help_command=None)

    async def setup_hook(self):
        # Database connect karna
        db.connect()

        # Agar cogs folder nahi hai toh auto-create karega
        if not os.path.exists('cogs'):
            os.makedirs('cogs')

        # Cogs folder ke andar ki saari python files load karega
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Loaded feature: {filename[:-3]}")

        # Slash Commands ko Discord pe sync karna
        await self.tree.sync()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'{Config.BOT_NAME} is online and ready!')
        await self.change_presence(activity=discord.Game(name=f"{Config.PREFIX}help | @{Config.BOT_NAME}"))

bot = GhotifyBot()

# Basic Error Handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Error", description="Bhai, tere paas ye command chalane ki permission nahi hai!", color=Config.COLOR_ERROR)
        await ctx.send(embed=embed)
    else:
        logger.error(f"Error in command: {error}")

if __name__ == "__main__":
    if not Config.TOKEN:
        logger.critical("Bhai, .env file me BOT_TOKEN daalna bhool gaya!")
    else:
        bot.run(Config.TOKEN)
              
