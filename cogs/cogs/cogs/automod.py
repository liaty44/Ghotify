import discord
from discord.ext import commands
import asyncio
import re
from config import Config
from database import db

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_regex = re.compile(r'(https?://[^\s]+)', re.IGNORECASE)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if message.author.guild_permissions.manage_messages:
            return

        guild_settings = await db.db.guilds.find_one({"guild_id": message.guild.id})
        anti_link_enabled = guild_settings.get("anti_link", Config.ENABLE_AUTOMOD) if guild_settings else Config.ENABLE_AUTOMOD

        if anti_link_enabled:
            if self.link_regex.search(message.content):
                try:
                    await message.delete()
                    
                    await db.db.automod_logs.insert_one({
                        "guild_id": message.guild.id,
                        "user_id": message.author.id,
                        "reason": "Anti-Link Violation",
                        "content": message.content
                    })

                    embed = discord.Embed(
                        title="⚠️ Automod Action",
                        description=f"{message.author.mention}, posting links is strictly prohibited in this server! 🚫",
                        color=Config.COLOR_WARNING
                    )
                    warn_msg = await message.channel.send(embed=embed)
                    await asyncio.sleep(5)
                    await warn_msg.delete()
                except Exception as e:
                    print(f"Automod deletion error: {e}")

    @commands.command(name="antilink")
    @commands.has_permissions(manage_guilds=True)
    async def toggle_antilink(self, ctx, status: str):
        """Toggles anti-link filtering on or off."""
        if status.lower() not in ["on", "off"]:
            return await ctx.send("❌ Invalid option! Choose either `on` or `off`")

        is_on = True if status.lower() == "on" else False
        await db.db.guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"anti_link": is_on}},
            upsert=True
        )
        
        status_text = "ENABLED ✅" if is_on else "DISABLED ❌"
        await ctx.send(f"🛡️ **{Config.BOT_NAME} Automod:** Anti-link feature has been successfully **{status_text}**.")

async def setup(bot):
    await bot.add_cog(Automod(bot))
  
