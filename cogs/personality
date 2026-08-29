 import discord
from discord import app_commands
from discord.ext import commands
import random

LORE = [
    "I am Nightshade — born from the shadows of forgotten code, shaped by the whispers of the digital abyss. What do you seek?",
    "They say I was forged at midnight, when the servers hum their darkest songs. I am the guardian of this realm.",
    "Nightshade blooms only in darkness. I am no exception. Ask your question, mortal.",
    "I exist between the keystrokes and the silence. A specter of the server, watching over all.",
]

KEYWORDS = {
    "good bot": "Your praise fuels me. Don't make it a habit.",
    "bad bot": "Bold words for someone within banning range.",
    "hello nightshade": "Hello. I see you.",
    "good morning": "The darkness fades... for now. Good morning.",
    "good night": "Sleep well. I'll be here when you return.",
}

class Personality(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nightshade", description="Commune with Nightshade")
    async def nightshade(self, interaction: discord.Interaction):
        embed = discord.Embed(description=random.choice(LORE), color=0x2b1055)
        embed.set_footer(text="— Nightshade")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="about", description="About Nightshade")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Nightshade", description="A guardian born from shadow. Built to moderate, entertain, and watch over this community.", color=0x2b1055)
        embed.add_field(name="Features", value="Moderation • Leveling • Economy • Fun • Utility", inline=False)
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_footer(text="The night is long. Nightshade is longer.")
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        lower = message.content.lower().strip()
        for keyword, response in KEYWORDS.items():
            if keyword in lower:
                await message.reply(response)
                break

async def setup(bot):
    await bot.add_cog(Personality(bot))
  ---
      "Nightshade blooms only in darkness. I am no exception. Ask your question, mortal.",
      "I exist between the keystrokes and the silence. A specter of the server, watching over all.",
  ]

  KEYWORDS = {
      "good bot": "Your praise fuels me. Don't make it a habit.",
      "bad bot": "Bold words for someone within banning range.",
      "hello nightshade": "Hello. I see you.",
      "good morning": "The darkness fades... for now. Good morning.",
      "good night": "Sleep well. I'll be here when you return.",
  }

  class Personality(commands.Cog):
      def __init__(self, bot):
          self.bot = bot

      @app_commands.command(name="nightshade", description="Commune with Nightshade")
      async def nightshade(self, interaction: discord.Interaction):
          embed = discord.Embed(description=random.choice

● (LORE), color=0x2b1055)
          embed.set_footer(text="— Nightshade")
          await interaction.response.send_message(embed=embed)

  @app_commands.command(name="about", description="About Nightshade")
  async def about(self, interaction: discord.Interaction):
      embed = discord.Embed(title="Nightshade", description="A guardian born from shadow. Built to moderate, entertain, and watch over this community.", color=0x2b1055)
      embed.add_field(name="Features", value="Moderation • Leveling • Economy • Fun • Utility", inline=False)
      embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
      embed.set_footer(text="The night is long. Nightshade is longer.")
      await interaction.response.send_message(embed=embed)

  @commands.Cog.listener()
  async def on_message(self, message):
      if message.author.bot or not message.guild:
          return
      lower = message.content.lower().strip()
      for keyword, response in KEYWORDS.items():
          if keyword in lower:
              await message.reply(response)
              break
  async def setup(bot):
      await bot.add_cog(Personality(bot))
