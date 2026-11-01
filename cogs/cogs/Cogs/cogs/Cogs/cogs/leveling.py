import discord
from discord.ext import commands
import random
from config import Config
from database import db

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        if not Config.ENABLE_LEVELING:
            return

        guild_id = message.guild.id
        user_id = message.author.id
        xp_gain = random.randint(15, 25)

        user_stats = await db.db.levels.find_one({"guild_id": guild_id, "user_id": user_id})
        
        if not user_stats:
            await db.db.levels.insert_one({"guild_id": guild_id, "user_id": user_id, "xp": xp_gain, "level": 0})
            return

        current_xp = user_stats.get("xp", 0) + xp_gain
        current_lvl = user_stats.get("level", 0)
        next_lvl_xp = 5 * (current_lvl ** 2) + (50 * current_lvl) + 100

        if current_xp >= next_lvl_xp:
            current_lvl += 1
            current_xp -= next_lvl_xp
            
            embed = discord.Embed(
                title="🎉 LEVEL UP! 🔥",
                description=f"Congratulations {message.author.mention}!\nYou have advanced to **Level `{current_lvl}`**!",
                color=Config.COLOR_SUCCESS
            )
            await message.channel.send(embed=embed)

        await db.db.levels.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"xp": current_xp, "level": current_lvl}}
        )

    @commands.command(name="rank")
    async def check_rank(self, ctx, member: discord.Member = None):
        """Displays your or another member's current rank stats."""
        member = member or ctx.author
        stats = await db.db.levels.find_one({"guild_id": ctx.guild.id, "user_id": member.id})

        if not stats:
            return await ctx.send("❌ This user has not earned any experience points yet.")

        level = stats.get("level", 0)
        xp = stats.get("xp", 0)
        next_lvl_xp = 5 * (level ** 2) + (50 * level) + 100

        embed = discord.Embed(
            title=f"📊 Rank Statistics: {member.name}",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(name="Current Level", value=f"`{level}`", inline=True)
        embed.add_field(name="XP Progress", value=f"`{xp}/{next_lvl_xp}` XP", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb"])
    async def show_leaderboard(self, ctx):
        """Displays the top 10 most active server members."""
        cursor = db.db.levels.find({"guild_id": ctx.guild.id}).sort("level", -1).sort("xp", -1).limit(10)
        results = await cursor.to_list(length=10)

        if not Antiquity := results:
            return await ctx.send("❌ The leaderboard is currently empty.")

        embed = discord.Embed(title=f"🏆 {ctx.guild.name} Server Leaderboard", color=Config.COLOR_PRIMARY)
        description = ""
        
        for index, data in enumerate(results):
            user = self.bot.get_user(data["user_id"])
            user_name = user.name if user else f"Unknown User ({data['user_id']})"
            description += f"**#{index+1}** | {user_name} — Level `{data['level']}` (XP: `{data['xp']}`)\n"

        embed.description = description
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
      
