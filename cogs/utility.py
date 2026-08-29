import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import asyncio
import re
from datetime import datetime, timedelta
from database import DB_PATH

TIME_RE = re.compile(r"(\d+)\s*(s|m|h|d)", re.IGNORECASE)

def parse_time(text):
    m = TIME_RE.search(text)
    if not m:
        return None
    v, u = int(m.group(1)), m.group(2).lower()
    return v * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.reminder_task = self.bot.loop.create_task(self.reminder_loop())

    async def cog_unload(self):
        self.reminder_task.cancel()

    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute("SELECT id, user_id, channel_id, message FROM reminders WHERE remind_at <= ?", (now,)) as cur:
                    rows = await cur.fetchall()
                for rid, user_id, channel_id, message in rows:
                    ch = self.bot.get_channel(channel_id)
                    if ch:
                        user = self.bot.get_user(user_id)
                        await ch.send(f"⏰ {user.mention if user else f'<@{user_id}>'} Reminder: {message}")
                    await db.execute("DELETE FROM reminders WHERE id = ?", (rid,))
                await db.commit()
            await asyncio.sleep(30)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT welcome_channel, welcome_message FROM guild_settings WHERE guild_id = ?", (member.guild.id,)) as cur:
                row = await cur.fetchone()
        if not row or not row[0]:
            return
        ch = member.guild.get_channel(row[0])
        if not ch:
            return
        msg = (row[1] or "Welcome {user} to {server}!").replace("{user}", member.mention).replace("{server}", member.guild.name)
        embed = discord.Embed(description=msg, color=0x7c3aed)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT goodbye_channel, goodbye_message FROM guild_settings WHERE guild_id = ?", (member.guild.id,)) as cur:
                row = await cur.fetchone()
        if not row or not row[0]:
            return
        ch = member.guild.get_channel(row[0])
        if not ch:
            return
        msg = (row[1] or "{user} has left {server}.").replace("{user}", str(member)).replace("{server}", member.guild.name)
        await ch.send(embed=discord.Embed(description=msg, color=0xff4444))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or str(reaction.emoji) != "⭐" or not reaction.message.guild:
            return
        guild_id = reaction.message.guild.id
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT starboard_channel, starboard_threshold FROM guild_settings WHERE guild_id = ?", (guild_id,)) as cur:
                row = await cur.fetchone()
        if not row or not row[0]:
            return
        if reaction.count < (row[1] or 3):
            return

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT star_message_id FROM starboard_posts WHERE guild_id = ? AND message_id = ?", (guild_id, reaction.message.id)) as cur:
                if await cur.fetchone():
                    return

        star_ch = reaction.message.guild.get_channel(row[0])
        if not star_ch:
            return

        embed = discord.Embed(description=reaction.message.content or "", color=0xffd700)
        embed.set_author(name=reaction.message.author.display_name, icon_url=reaction.message.author.display_avatar.url)
        embed.add_field(name="Original", value=f"[Jump]({reaction.message.jump_url})")
        if reaction.message.attachments:
            embed.set_image(url=reaction.message.attachments[0].url)
        embed.set_footer(text=f"⭐ {reaction.count} | #{reaction.message.channel.name}")
        star_msg = await star_ch.send(embed=embed)

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO starboard_posts VALUES (?, ?, ?)", (guild_id, reaction.message.id, star_msg.id))
            await db.commit()

    @app_commands.command(name="serverinfo", description="View server information")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=g.name, color=0x7c3aed)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="Owner", value=g.owner.mention if g.owner else "Unknown")
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Channels", value=str(len(g.channels)))
        embed.add_field(name="Roles", value=str(len(g.roles)))
        embed.add_field(name="Created", value=discord.utils.format_dt(g.created_at, style="D"))
        embed.add_field(name="Boost Level", value=str(g.premium_tier))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="View user information")
    @app_commands.describe(member="Member to look up")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        m = member or interaction.user
        embed = discord.Embed(title=str(m), color=m.color)
        embed.set_thumbnail(url=m.display_avatar.url)
        embed.add_field(name="ID", value=str(m.id))
        embed.add_field(name="Nickname", value=m.nick or "None")
        embed.add_field(name="Joined", value=discord.utils.format_dt(m.joined_at, style="D") if m.joined_at else "Unknown")
        embed.add_field(name="Created", value=discord.utils.format_dt(m.created_at, style="D"))
        roles = [r.mention for r in m.roles[1:]]
        embed.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles) or "None", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(time="When (e.g. 10m, 2h, 1d)", message="What to remind you about")
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        seconds = parse_time(time)
        if not seconds:
            return await interaction.response.send_message("Invalid format. Use: 30s, 10m, 2h, 1d", ephemeral=True)
        remind_at = (datetime.utcnow() + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO reminders (user_id, channel_id, message, remind_at) VALUES (?, ?, ?, ?)",
                             (interaction.user.id, interaction.channel_id, message, remind_at))
            await db.commit()
        await interaction.response.send_message(f"Got it! I'll remind you in **{time}**.", ephemeral=True)

    @app_commands.command(name="setup", description="Configure Nightshade for this server")
    @app_commands.describe(
        log_channel="Channel for mod logs",
        welcome_channel="Channel for welcome messages",
        goodbye_channel="Channel for goodbye messages",
        starboard_channel="Channel for the starboard",
        level_up_channel="Channel for level-up announcements"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction,
                    log_channel: discord.TextChannel = None,
                    welcome_channel: discord.TextChannel = None,
                    goodbye_channel: discord.TextChannel = None,
                    starboard_channel: discord.TextChannel = None,
                    level_up_channel: discord.TextChannel = None):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO guild_settings (guild_id, log_channel, welcome_channel, goodbye_channel, starboard_channel, level_up_channel)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    log_channel = COALESCE(?, log_channel),
                    welcome_channel = COALESCE(?, welcome_channel),
                    goodbye_channel = COALESCE(?, goodbye_channel),
                    starboard_channel = COALESCE(?, starboard_channel),
                    level_up_channel = COALESCE(?, level_up_channel)
            """, (
                interaction.guild_id,
                log_channel.id if log_channel else None,
                welcome_channel.id if welcome_channel else None,
                goodbye_channel.id if goodbye_channel else None,
                starboard_channel.id if starboard_channel else None,
                level_up_channel.id if level_up_channel else None,
                log_channel.id if log_channel else None,
                welcome_channel.id if welcome_channel else None,
                goodbye_channel.id if goodbye_channel else None,
                starboard_channel.id if starboard_channel else None,
                level_up_channel.id if level_up_channel else None,
            ))
            await db.commit()

        embed = discord.Embed(title="Nightshade Setup Updated", color=0x7c3aed)
        for name, ch in [("Log", log_channel), ("Welcome", welcome_channel), ("Goodbye", goodbye_channel), ("Starboard", starboard_channel), ("Level-Up", level_up_channel)]:
            if ch:
                embed.add_field(name=f"{name} Channel", value=ch.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ticket", description="Open a support ticket")
    @app_commands.describe(reason="What do you need help with?")
    async def ticket(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        try:
            thread = await interaction.channel.create_thread(
                name=f"ticket-{interaction.user.name}",
                type=discord.ChannelType.private_thread
            )
            await thread.add_user(interaction.user)
            embed = discord.Embed(title="Support Ticket", color=0x7c3aed,
                                  description=f"Hello {interaction.user.mention}! Staff will be with you shortly.\n\n**Reason:** {reason}")
            await thread.send(embed=embed)
            await interaction.response.send_message(f"Ticket created: {thread.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to create private threads here.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
