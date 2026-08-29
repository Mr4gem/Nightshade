import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from database import init_db

load_dotenv()

  intents = discord.Intents.all()
  bot = commands.Bot(command_prefix="!", intents=intents)

  COGS = ["moderation", "fun", "leveling", "economy", "utility", "personality"]

  @bot.event
  async def on_ready():
      await bot.tree.sync()
      print(f"Nightshade online as {bot.user} (ID: {bot.user.id})")

  async def main():
      await init_db()
      async with bot:
          for cog in COGS:
              await bot.load_extension(f"cogs.{cog}")
          await bot.start(os.getenv("DISCORD_TOKEN"))

  asyncio.run(main())
