import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import random
import time
from database import DB_PATH

XP_RANGE = (15, 25)
XP_COOLDOWN = 60

def xp_for_level(level):
    return level * 100

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        now = time.time()
        key = (message.guild.id, message.author.id)
        if now - self.cooldowns.get(key, 0) < XP_COOLDOWN:
            return
        self.cooldowns[key] = now

        xp_gain = random.randint(*XP_RANGE)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO levels (guild_id, user_id, xp) VALUES (?, ?, ?) ON CONFLICT(guild_id, user_id) DO UPDATE SET xp = xp + ?",
                (message.guild.id, message.author.id, xp_gain, xp_gain)
            )
            await db.commit()

            async with db.execute(
                "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
                (message.guild.id, message.author.id)
            ) as cur:
                xp, level = await cur.fetchone()

            required = xp_for_level(level + 1)
            if xp >= required:
                new_level = level + 1
                await db.execute(
                    "UPDATE levels SET level = ?, xp = xp - ? WHERE guild_id = ? AND user_id = ?",
                    (new_level, required, message.guild.id, message.author.id)
                )
                await db.commit()

                async with db.execute("SELECT level_up_channel FROM guild_settings WHERE guild_id = ?", (message.guild.id,)) as cur:
                    row = await cur.fetchone()

                channel = message.channel
                if row and row[0]:
                    ch = message.guild.get_channel(row[0])
                    if ch:
                        channel = ch

                embed = discord.Embed(
                    title="Level Up!",
                    description=f"{message.author.mention} reached **Level {new_level}**!",
                    color=0x7c3aed
                )
                await channel.send(embed=embed)

    @app_commands.command(name="rank", description="Check your rank")
    @app_commands.describe(member="Member to check (defaults to you)")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
                (interaction.guild_id, target.id)
            ) as cur:
                row = await cur.fetchone()

        if not row:
            return await interaction.response.send_message(f"{target.mention} hasn't earned any XP yet.", ephemeral=True)

        xp, level = row
        required = xp_for_level(level + 1)
        filled = int((xp / required) * 20)
        bar = "█" * filled + "░" * (20 - filled)

        embed = discord.Embed(title=f"{target.display_name}'s Rank", color=0x7c3aed)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Level", value=str(level))
        embed.add_field(name="XP", value=f"{xp} / {required}")
        embed.add_field(name="Progress", value=f"`{bar}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT user_id, level, xp FROM levels WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT 10",
                (interaction.guild_id,)
            ) as cur:
                rows = await cur.fetchall()

        if not rows:
            return await interaction.response.send_message("No one has earned XP yet.", ephemeral=True)

        medals = ["🥇","🥈","🥉"]
        lines = []
        for i, (user_id, level, xp) in enumerate(rows):
            prefix = medals[i] if i < 3 else f"{i+1}."
            m = interaction.guild.get_member(user_id)
            name = m.display_name if m else f"User {user_id}"
            lines.append(f"{prefix} **{name}** — Level {level} ({xp} XP)")

        embed = discord.Embed(title="XP Leaderboard", description="\n".join(lines), color=0x7c3aed)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
