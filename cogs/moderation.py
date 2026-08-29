import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import time
import re
from datetime import timedelta
from database import DB_PATH

BAD_WORDS = []  # add words you want filtered
INVITE_PATTERN = re.compile(r"discord\.gg/\S+|discord\.com/invite/\S+", re.IGNORECASE)
SPAM_THRESHOLD = 5
SPAM_WINDOW = 5

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = {}

    async def get_log_channel(self, guild_id):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT log_channel FROM guild_settings WHERE guild_id = ?", (guild_id,)) as cur:
                row = await cur.fetchone()
        return row[0] if row else None

    async def log_action(self, guild, embed):
        log_id = await self.get_log_channel(guild.id)
        if log_id:
            ch = guild.get_channel(log_id)
            if ch:
                await ch.send(embed=embed)

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't kick someone with an equal or higher role.", ephemeral=True)
        await member.kick(reason=reason)
        embed = discord.Embed(title="Member Kicked", color=0xff4444)
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
        await self.log_action(interaction.guild, embed)

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason", delete_days="Days of messages to delete")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't ban someone with an equal or higher role.", ephemeral=True)
        await member.ban(reason=reason, delete_message_days=delete_days)
        embed = discord.Embed(title="Member Banned", color=0xff0000)
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
        await self.log_action(interaction.guild, embed)

    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.describe(user_id="User ID to unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"Unbanned {user}.")
        except (ValueError, discord.NotFound):
            await interaction.response.send_message("User not found or not banned.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't timeout someone with an equal or higher role.", ephemeral=True)
        await member.timeout(timedelta(minutes=minutes), reason=reason)
        embed = discord.Embed(title="Member Timed Out", color=0xffa500)
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Duration", value=f"{minutes} minutes")
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
        await self.log_action(interaction.guild, embed)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO warnings (guild_id, user_id, mod_id, reason) VALUES (?, ?, ?, ?)",
                (interaction.guild_id, member.id, interaction.user.id, reason)
            )
            await db.commit()
            async with db.execute(
                "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
                (interaction.guild_id, member.id)
            ) as cur:
                count = (await cur.fetchone())[0]

        embed = discord.Embed(title="Member Warned", color=0xffcc00)
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Total Warnings", value=str(count))
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
        await self.log_action(interaction.guild, embed)

        if count >= 5:
            await member.ban(reason="Auto-ban: 5 warnings")
            await interaction.channel.send(f"{member.mention} has been auto-banned for reaching 5 warnings.")
        elif count >= 3:
            await member.timeout(timedelta(hours=1), reason="Auto-timeout: 3 warnings")
            await interaction.channel.send(f"{member.mention} has been auto-timed out for reaching 3 warnings.")

    @app_commands.command(name="warnings", description="View warnings for a member")
    @app_commands.describe(member="Member to check")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT reason, timestamp FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC LIMIT 10",
                (interaction.guild_id, member.id)
            ) as cur:
                rows = await cur.fetchall()

        if not rows:
            return await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)

        embed = discord.Embed(title=f"Warnings for {member}", color=0xffcc00)
        for i, (reason, ts) in enumerate(rows, 1):
            embed.add_field(name=f"Warning {i} — {ts[:10]}", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarns", description="Clear all warnings for a member")
    @app_commands.describe(member="Member to clear warnings for")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, member.id))
            await db.commit()
        await interaction.response.send_message(f"Cleared all warnings for {member.mention}.")

    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if not 1 <= amount <= 100:
            return await interaction.response.send_message("Amount must be between 1 and 100.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT automod_enabled FROM guild_settings WHERE guild_id = ?", (message.guild.id,)) as cur:
                row = await cur.fetchone()
        if row and not row[0]:
            return

        now = time.time()
        uid = message.author.id
        self.message_cache.setdefault(uid, [])
        self.message_cache[uid] = [t for t in self.message_cache[uid] if now - t < SPAM_WINDOW]
        self.message_cache[uid].append(now)

        if len(self.message_cache[uid]) >= SPAM_THRESHOLD:
            await message.delete()
            await message.channel.send(f"{message.author.mention} slow down.", delete_after=5)
            self.message_cache[uid] = []
            return

        if INVITE_PATTERN.search(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention} invite links are not allowed.", delete_after=5)
            return

        if BAD_WORDS and any(w in message.content.lower() for w in BAD_WORDS):
            await message.delete()
            await message.channel.send(f"{message.author.mention} watch your language.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
