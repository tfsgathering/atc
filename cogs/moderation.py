import discord
from discord.ext import commands
import datetime


def nowtime() -> str:
    """Returns current UTC timestamp as string"""
    
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')


class Moderation(commands.Cog):
    """Moderation commands with logging support"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_log(self, ctx: commands.Context, logmsg: str):
        """Send log messages to the configured log channel"""
        
        try:
            guild_id = str(ctx.guild.id)
            log_channel = self.bot.get_channel(self.bot.logchannel)

            if log_channel is not None:
                await log_channel.send(logmsg)
            else:
                await ctx.send(":warning: Log channel not found.")
        except Exception as e:
            await ctx.send(f":warning: Error while logging: {e}")

    @commands.command(aliases=["nick", "setnick"])
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """Change or reset a user's nickname."""
        
        try:
            await member.edit(nick=name)
            msg = f"Changed **{member.name}**'s nickname to **{name}**." if name else f"Reset **{member.name}**'s nickname."
            await ctx.send(msg)

            logmsg = f":pencil: `{nowtime()}`\n**{ctx.author}** changed **{member}**'s nickname to **{name or 'reset'}**."
            await self.send_log(ctx, logmsg)
        except Exception as e:
            await ctx.send(f"⚠:warning: {e}")

    @commands.command(aliases=["mute", "quiet"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str = "10m", *, reason: str = None):
        """Timeout a user for a specified duration (s/m/h/d)."""
        
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        value = duration[:-1]

        if unit not in units or not value.isdigit():
            return await ctx.send("Invalid duration. Use format like `10m`, `2h`, etc.")

        seconds = int(value) * units[unit]
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)

        reason = f"({ctx.author}) {reason or 'N/A'}"
        try:
            await member.timeout(until, reason=reason)
            await ctx.send(f"Timed out **{member}** for {duration}. Reason: {reason}")

            logmsg = f":mute: `{nowtime()}`\n**{ctx.author}** timed out **{member}** for {duration}. Reason: {reason}"
            await self.send_log(ctx, logmsg)
        except Exception as e:
            await ctx.send(f"⚠:warning: {e}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        
        """Kick a member."""
        reason = f"({ctx.author}) {reason or 'N/A'}"
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Kicked **{member}**. Reason: {reason}")

            logmsg = f":boot: `{nowtime()}`\n**{ctx.author}** kicked **{member}**. Reason: {reason}"
            await self.send_log(ctx, logmsg)
        except Exception as e:
            await ctx.send(f":warning: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        """Ban a member."""
        reason = f"({ctx.author}) {reason or 'N/A'}"
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Banned **{member}**. Reason: {reason}")

            logmsg = f":hammer: `{nowtime()}`\n**{ctx.author}** banned **{member}**. Reason: {reason}"
            await self.send_log(ctx, logmsg)
        except Exception as e:
            await ctx.send(f":warning: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason: str = None):
        """Unban a user by ID/mention."""
        reason = f"({ctx.author}) {reason or 'N/A'}"
        try:
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"Unbanned **{user}**. Reason: {reason}")

            logmsg = f":o: `{nowtime()}`\n**{ctx.author}** unbanned **{user}**. Reason: {reason}"
            await self.send_log(ctx, logmsg)
        except Exception as e:
            await ctx.send(f":warning: {e}")

    @commands.command(aliases=["clear", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, number: int = 1):
        """Delete a given number of messages (up to 200 for admins, 50 for others)."""
        limit = 200 if ctx.author.guild_permissions.administrator else 50

        if number <= 0 or number > limit:
            return await ctx.send(f":warning: You can only delete up to {limit} messages at once.")

        try:
            deleted = await ctx.channel.purge(limit=number + 1)
            await ctx.send(f"Deleted {len(deleted)-1} messages.", delete_after=5)

            logmsg = f":wastebasket: `{nowtime()}`\n**{ctx.author}** deleted {len(deleted)-1} messages in {ctx.channel.mention}."
            await self.send_log(ctx, logmsg)
        except Exception as e:
            await ctx.send(f":warning: {e}")

    @commands.command(aliases=["lock"])
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        """Toggle channel lock/unlock."""
        channel = channel or ctx.channel
        try:
            perms = channel.overwrites_for(ctx.guild.default_role)
            if perms.send_messages is False:
                perms.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
                await ctx.send(f":unlock: Unlocked {channel.mention}.")
                await self.send_log(ctx, f":unlock: `{nowtime()}`\n**{ctx.author}** unlocked {channel.mention}.")
            else:
                perms.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
                await ctx.send(f":lock: Locked {channel.mention}.")
                await self.send_log(ctx, f":lock: `{nowtime()}`\n**{ctx.author}** locked {channel.mention}.")
        except Exception as e:
            await ctx.send(f":warning: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
