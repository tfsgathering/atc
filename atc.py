import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class ATCBot(commands.Bot):
    async def setup_hook(self):
        await load_cogs(self)
        await self.tree.sync()


bot = ATCBot(command_prefix=".", intents=intents)
bot.logchannel = 1175377575485378570
bot.apixkey = os.getenv("X-API-KEY")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} with ID: {bot.user.id}")


async def load_cogs(bot):
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"Loaded cog: {cog_name}")
            except commands.errors.NoEntryPointError:
                print(f"Skipped {cog_name}")


async def main():
    async with bot:
        await bot.start(os.getenv("TOKEN_ATC"))

import asyncio

if __name__ == "__main__":
    asyncio.run(main())
