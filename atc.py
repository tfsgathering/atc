import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)
bot.logchannel = 1175377575485378570
bot.apixkey = os.getenv("X-ENV-KEY")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} with ID: {bot.user.id}")

async def load_cogs():
    """Load all cogs in the cogs folder, skipping non-cog files."""
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"Loaded cog: {cog_name}")
            except commands.errors.NoEntryPointError:
                print(f"Skipped {cog_name}, no setup function found.")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
