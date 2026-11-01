import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from config import Config
from database import db

class TicketView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Create Ticket 📩", style=discord.ButtonStyle.primary, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        ticket_config = await db.db.tickets.find_one({"guild_id": guild.id})
        ticket_count = ticket_config.get("count", 0) if ticket_config else 0
        ticket_count += 1

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{ticket_count:04d}",
            overwrites=overwrites,
            topic=f"Ticket opened by {user.name} (ID: {user.id})"
        )

        await db.db.tickets.update_one(
            {"guild_id": guild.id},
            {"$set": {"count": ticket_count}},
            upsert=True
        )

        close_view = View(timeout=None)
        close_btn = Button(label="Close Ticket 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
        
        async def close_callback(inter: discord.Interaction):
            await inter.response.send_message("This ticket will be deleted in 5 seconds...")
            await asyncio.sleep(5)
            await inter.channel.delete()

        close_btn.callback = close_callback
        close_view.add_item(close_btn)

        embed = discord.Embed(
            title=f"Ticket #{ticket_count:04d}",
            description=f"Hello {user.mention},\nOur support team will assist you shortly. Click the button below to close this ticket.",
            color=Config.COLOR_PRIMARY
        )
        await channel.send(embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ Ticket created successfully: {channel.mention}", ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView(self.bot))

    @commands.command(name="ticketsetup")
    @commands.has_permissions(manage_guilds=True)
    async def setup_ticket_panel(self, ctx):
        """Sets up the interactive ticket panel inside the server."""
        embed = discord.Embed(
            title="🎫 Support Ticket Panel",
            description="If you require assistance or need to get in touch with staff, click the button below to open a ticket channel.",
            color=Config.COLOR_PRIMARY
        )
        view = TicketView(self.bot)
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Ticket(bot))
  
