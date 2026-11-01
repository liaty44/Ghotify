import discord
from discord.ext import commands
from config import Config
from database import db

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            self.invites[guild.id] = await guild.invites()
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if guild.id not in self.invites:
            return

        old_invites = self.invites[guild.id]
        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            return

        inviter = None
        used_invite = None

        for invite in old_invites:
            for new_invite in new_invites:
                if invite.code == new_invite.code and new_invite.uses > invite.uses:
                    inviter = new_invite.inviter
                    used_invite = new_invite
                    break

        self.invites[guild.id] = new_invites

        if inviter:
            await db.db.invites.update_one(
                {"guild_id": guild.id, "user_id": inviter.id},
                {"$inc": {"joins": 1}},
                upsert=True
            )

            user_data = await db.db.invites.find_one({"guild_id": guild.id, "user_id": inviter.id})
            total_invites = user_data.get("joins", 1) if user_data else 1
            print(f"[Invites] {member.name} joined using code {used_invite.code} by {inviter.name} (Total: {total_invites})")

    @commands.command(name="invites")
    async def show_invites(self, ctx, member: discord.Member = None):
        """Displays invite statistics for a user."""
        member = member or ctx.author
        user_data = await db.db.invites.find_one({"guild_id": ctx.guild.id, "user_id": member.id})
        
        joins = user_data.get("joins", 0) if user_data else 0
        
        embed = discord.Embed(
            title=f"📊 Invite Stats: {member.name}",
            description=f"This user has invited a total of **{joins}** members to the server! 🔥",
            color=Config.COLOR_PRIMARY
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
  
