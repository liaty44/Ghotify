import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import asyncio
import random
import time
from config import Config
from database import db

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @commands.command(name="gstart")
    @has_permissions(manage_guilds=True)
    async def start_giveaway(self, ctx, duration: str, winners_count: int, *, prize: str):
        """Starts an automated giveaway. Usage: gstart 10m 1 Nitro Premium"""
        time_unit = duration[-1].lower()
        try:
            time_val = int(duration[:-1])
        except ValueError:
            return await ctx.send("❌ Invalid duration format! Use format like: 10m, 2h, 1d")

        if time_unit == 'm':
            seconds = time_val * 60
        elif time_unit == 'h':
            seconds = time_val * 3600
        elif time_unit == 'd':
            seconds = time_val * 86400
        else:
            return await ctx.send("❌ Invalid time unit! Please use 'm' (minutes), 'h' (hours), or 'd' (days).")

        end_time = time.time() + seconds

        embed = discord.Embed(
            title=f"🎉 GIVEAWAY: {prize} 🎉",
            description=f"React with 🎉 to enter!\n\n**Winners:** {winners_count}\n**Ends:** <t:{int(end_time)}:R>",
            color=Config.COLOR_PRIMARY
        )
        embed.set_footer(text=f"Hosted by {ctx.author.name}")
        
        g_message = await ctx.send(embed=embed)
        await g_message.add_reaction("🎉")

        await db.db.giveaways.insert_one({
            "message_id": g_message.id,
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "prize": prize,
            "winners": winners_count,
            "end_time": end_time,
            "ended": False
        })

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        current_time = time.time()
        active_giveaways = db.db.giveaways.find({"end_time": {"$lte": current_time}, "ended": False})
        
        async for g in active_giveaways:
            channel = self.bot.get_channel(g["channel_id"])
            if not channel:
                continue
            try:
                message = await channel.fetch_message(g["message_id"])
                reaction = discord.utils.get(message.reactions, emoji="🎉")
                users = [user async for user in reaction.users() if not user.bot]

                if len(users) < g["winners"]:
                    winners = users
                else:
                    winners = random.sample(users, g["winners"])

                if not winners:
                    await channel.send(f"😭 **Giveaway Ended!** No valid entries were found for **{g['prize']}**.")
                else:
                    winner_mentions = ", ".join([w.mention for w in winners])
                    await channel.send(f"🎉 **GIVEAWAY ENDED!** 🎉\nCongratulations {winner_mentions}! You have won **{g['prize']}**!")
                    
                    end_embed = message.embeds[0]
                    end_embed.description = f"**Giveaway Ended!**\n\n**Winners:** {winner_mentions}"
                    end_embed.color = Config.COLOR_SUCCESS
                    await message.edit(embed=end_embed)

            except Exception as e:
                print(f"Giveaway error processing: {e}")
            
            await db.db.giveaways.update_one({"message_id": g["message_id"]}, {"$set": {"ended": True}})

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
      
