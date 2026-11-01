import discord
from discord.ext import commands
from config import Config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kicks a member from the server."""
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="Member Kicked",
            description=f"**{member.name}** has been successfully kicked.\n**Reason:** {reason}",
            color=Config.COLOR_SUCCESS
        )
        await ctx.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Bans a member from the server."""
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="Member Banned",
            description=f"**{member.name}** has been permanently banned.\n**Reason:** {reason}",
            color=Config.COLOR_ERROR
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
      
