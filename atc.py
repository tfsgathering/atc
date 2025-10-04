import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".",
                   intents=intents)

bot.logchannel = 1175377575485378570

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} with ID: {bot.user.id}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("TOKEN"))

import asyncio
asyncio.run(main())
