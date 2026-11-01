import discord
from discord.ext import commands
from config import Config
from database import db

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = await db.db.guilds.find_one({"guild_id": member.guild.id})
        if not settings or "welcome_channel" not in settings:
            return

        channel = member.guild.get_channel(settings["welcome_channel"])
        if channel:
            embed = discord.Embed(
                title=f"👋 Welcome to {member.guild.name}!",
                description=f"Hello {member.mention}, thank you for joining us!\nWe are now up to **{member.guild.member_count}** members! 🔥",
                color=Config.COLOR_SUCCESS
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    @commands.command(name="setwelcome")
    @commands.has_permissions(manage_guilds=True)
    async def configure_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Configures the text channel where welcome messages are logged."""
        await db.db.guilds.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"welcome_channel": channel.id}},
            upsert=True
        )
        await ctx.send(f"✅ Welcome channel has been successfully updated to: {channel.mention}")

    @commands.command(name="ping")
    async def ping_check(self, ctx):
        """Checks the API latency of the bot."""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**{Config.BOT_NAME} Gateway Latency:** `{latency}ms`",
            color=Config.COLOR_PRIMARY
        )
        await ctx.send(embed=embed)

    @commands.command(name="help")
    async def custom_help(self, ctx):
        """Displays the command dashboard panel."""
        embed = discord.Embed(
            title=f"🛠️ {Config.BOT_NAME} Command Panel",
            description=f"The current bot prefix is `{Config.PREFIX}`. Available command systems are listed below:",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(name="🛡️ Moderation Tools", value="`kick`, `ban`", inline=False)
        embed.add_field(name="🎉 Giveaway Engine", value="`gstart`", inline=False)
        embed.add_field(name="📊 Invite Tracking", value="`invites`", inline=False)
        embed.add_field(name="🛡️ Automated Filters", value="`antilink`", inline=False)
        embed.add_field(name="🎫 Help Desk Tickets", value="`ticketsetup`", inline=False)
        embed.add_field(name="🏆 Member Rankings", value="`rank`, `leaderboard`", inline=False)
        embed.add_field(name="⚙️ Config Tools", value="`setwelcome`, `ping`", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
  
