import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import random
from datetime import date
from database import DB_PATH

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_balance(self, guild_id, user_id):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT coins FROM economy WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)) as cur:
                row = await cur.fetchone()
        return row[0] if row else 0

    async def update_balance(self, guild_id, user_id, amount):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO economy (guild_id, user_id, coins) VALUES (?, ?, 0) ON CONFLICT(guild_id, user_id) DO NOTHING",
                (guild_id, user_id)
            )
            await db.execute(
                "UPDATE economy SET coins = MAX(0, coins + ?) WHERE guild_id = ? AND user_id = ?",
                (amount, guild_id, user_id)
            )
            await db.commit()

    @app_commands.command(name="balance", description="Check your coin balance")
    @app_commands.describe(member="Check another user's balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        coins = await self.get_balance(interaction.guild_id, target.id)
        embed = discord.Embed(color=0xffd700)
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        embed.add_field(name="Balance", value=f"🪙 {coins:,} coins")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        today = str(date.today())
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT last_daily FROM economy WHERE guild_id = ? AND user_id = ?",
                (interaction.guild_id, interaction.user.id)
            ) as cur:
                row = await cur.fetchone()
        if row and row[0] == today:
            return await interaction.response.send_message("Already claimed today. Come back tomorrow!", ephemeral=True)
        amount = random.randint(500, 1000)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO economy (guild_id, user_id, coins, last_daily) VALUES (?, ?, ?, ?) ON CONFLICT(guild_id, user_id) DO UPDATE SET coins = coins + ?, last_daily = ?",
                (interaction.guild_id, interaction.user.id, amount, today, amount, today)
            )
            await db.commit()
        embed = discord.Embed(title="Daily Reward!", description=f"You received **🪙 {amount:,} coins**!", color=0xffd700)
        embed.set_footer(text="Come back tomorrow for more.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gamble", description="Gamble your coins")
    @app_commands.describe(amount="Amount to gamble")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            return await interaction.response.send_message("Bet a positive amount.", ephemeral=True)
        balance = await self.get_balance(interaction.guild_id, interaction.user.id)
        if amount > balance:
            return await interaction.response.send_message(f"You only have 🪙 {balance:,}.", ephemeral=True)
        if random.random() < 0.45:
            winnings = int(amount * 1.8)
            net = winnings - amount
            await self.update_balance(interaction.guild_id, interaction.user.id, net)
            embed = discord.Embed(title="You Won!", description=f"You won **🪙 {winnings:,}** (net +{net:,})!", color=0x00ff00)
        else:
            await self.update_balance(interaction.guild_id, interaction.user.id, -amount)
            embed = discord.Embed(title="You Lost.", description=f"You lost **🪙 {amount:,}**.", color=0xff4444)
        new_bal = await self.get_balance(interaction.guild_id, interaction.user.id)
        embed.set_footer(text=f"Balance: 🪙 {new_bal:,}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="give", description="Give coins to another user")
    @app_commands.describe(member="Who to give to", amount="Amount to give")
    async def give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if member.bot or member == interaction.user:
            return await interaction.response.send_message("Invalid target.", ephemeral=True)
        if amount <= 0:
            return await interaction.response.send_message("Give a positive amount.", ephemeral=True)
        balance = await self.get_balance(interaction.guild_id, interaction.user.id)
        if amount > balance:
            return await interaction.response.send_message(f"You only have 🪙 {balance:,}.", ephemeral=True)
        await self.update_balance(interaction.guild_id, interaction.user.id, -amount)
        await self.update_balance(interaction.guild_id, member.id, amount)
        await interaction.response.send_message(f"Gave **🪙 {amount:,} coins** to {member.mention}.")

    @app_commands.command(name="richlist", description="See the richest members")
    async def richlist(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT user_id, coins FROM economy WHERE guild_id = ? ORDER BY coins DESC LIMIT 10",
                (interaction.guild_id,)
            ) as cur:
                rows = await cur.fetchall()
        if not rows:
            return await interaction.response.send_message("No one has any coins yet.", ephemeral=True)
        medals = ["🥇","🥈","🥉"]
        lines = []
        for i, (user_id, coins) in enumerate(rows):
            prefix = medals[i] if i < 3 else f"{i+1}."
            m = interaction.guild.get_member(user_id)
            name = m.display_name if m else f"User {user_id}"
            lines.append(f"{prefix} **{name}** — 🪙 {coins:,}")
        embed = discord.Embed(title="Richest Members", description="\n".join(lines), color=0xffd700)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))