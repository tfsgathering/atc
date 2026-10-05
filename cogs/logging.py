import asyncio
import datetime

import discord
from discord.ext import commands

from .helpers import send_log


def clip(text: str, limit: int = 300) -> str:
    text = discord.utils.escape_mentions(text or "[no text]")
    return text if len(text) <= limit else text[:limit] + "..."


class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not after.guild or after.author.bot or before.content == after.content:
            return

        await send_log(
            self.bot,
            ":pencil2:",
            f"**{after.author}** edited a message in {after.channel.mention}.\n"
            f"Before: {clip(before.content)}\n"
            f"After: {clip(after.content)}"
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        await send_log(
            self.bot,
            ":wastebasket:",
            f"**{message.author}**'s message was deleted in {message.channel.mention}.\n"
            f"Content: {clip(message.content)}"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Give the audit log a moment to register kicks/bans
        await asyncio.sleep(1)

        now = discord.utils.utcnow()

        for action, emoji, verb in (
            (discord.AuditLogAction.ban, ":hammer:", "banned"),
            (discord.AuditLogAction.kick, ":boot:", "kicked"),
        ):
            try:
                async for entry in member.guild.audit_logs(limit=5, action=action):
                    if entry.target.id != member.id:
                        continue
                    if (now - entry.created_at) > datetime.timedelta(seconds=15):
                        continue

                    await send_log(
                        self.bot,
                        emoji,
                        f"**{member}** was {verb} by **{entry.user}**. Reason: {entry.reason or 'N/A'}"
                    )
                    return

            except discord.Forbidden:
                break

        await send_log(
            self.bot,
            ":door:",
            f"**{member}** left the server."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
