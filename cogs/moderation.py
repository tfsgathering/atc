import discord
from discord.ext import commands
from discord import app_commands
import datetime


def nowtime():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_log(self, interaction: discord.Interaction, logmsg: str):
        try:
            log_channel = self.bot.get_channel(self.bot.logchannel)
            if log_channel:
                await log_channel.send(logmsg)
        except Exception:
            pass
        
    @app_commands.command(name="nickname", description="Change or reset nickname")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nickname(self, interaction: discord.Interaction, member: discord.Member, name: str = None):
        try:
            await member.edit(nick=name)

            msg = f"Changed **{member.name}**'s nickname to **{name}**." if name else f"Reset **{member.name}**'s nickname."
            await interaction.response.send_message(msg)

            logmsg = f":pencil: `{nowtime()}`\n**{interaction.user}** changed **{member}**'s nickname to **{name or 'reset'}**."
            await self.send_log(interaction, logmsg)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}

        unit = duration[-1]
        value = duration[:-1]

        if unit not in units or not value.isdigit():
            await interaction.response.send_message("Invalid duration (e.g. 10m, 2h)", ephemeral=True)
            return

        seconds = int(value) * units[unit]
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)

        reason = f"({interaction.user}) {reason or 'N/A'}"

        try:
            await member.timeout(until, reason=reason)
            await interaction.response.send_message(f"Timed out **{member}** for {duration}")

            logmsg = f":mute: `{nowtime()}`\n**{interaction.user}** timed out **{member}** for {duration}. Reason: {reason}"
            await self.send_log(interaction, logmsg)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        reason = f"({interaction.user}) {reason or 'N/A'}"

        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"Kicked **{member}**")

            logmsg = f":boot: `{nowtime()}`\n**{interaction.user}** kicked **{member}**. Reason: {reason}"
            await self.send_log(interaction, logmsg)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        reason = f"({interaction.user}) {reason or 'N/A'}"

        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"Banned **{member}**")

            logmsg = f":hammer: `{nowtime()}`\n**{interaction.user}** banned **{member}**. Reason: {reason}"
            await self.send_log(interaction, logmsg)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        reason = f"({interaction.user}) {reason or 'N/A'}"

        try:
            await interaction.guild.unban(user, reason=reason)
            await interaction.response.send_message(f"Unbanned **{user}**")

            logmsg = f":o: `{nowtime()}`\n**{interaction.user}** unbanned **{user}**. Reason: {reason}"
            await self.send_log(interaction, logmsg)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, number: int):
        limit = 200 if interaction.user.guild_permissions.administrator else 50

        if number <= 0 or number > limit:
            await interaction.response.send_message(f"Limit: {limit}", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=number)
            await interaction.followup.send(f"Deleted {len(deleted)} messages", ephemeral=True)

            logmsg = f":wastebasket: `{nowtime()}`\n**{interaction.user}** deleted {len(deleted)} messages in {interaction.channel.mention}"
            await self.send_log(interaction, logmsg)

        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="lockdown", description="Toggle channel lock")
    async def lockdown(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        channel = channel or interaction.channel

        try:
            perms = channel.overwrites_for(interaction.guild.default_role)

            if perms.send_messages is False:
                perms.send_messages = None
                await channel.set_permissions(interaction.guild.default_role, overwrite=perms)
                await interaction.response.send_message(f"Unlocked {channel.mention}")
                await self.send_log(interaction, f":unlock: `{nowtime()}`\n**{interaction.user}** unlocked {channel.mention}")
            else:
                perms.send_messages = False
                await channel.set_permissions(interaction.guild.default_role, overwrite=perms)
                await interaction.response.send_message(f"Locked {channel.mention}")
                await self.send_log(interaction, f":lock: `{nowtime()}`\n**{interaction.user}** locked {channel.mention}")

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
