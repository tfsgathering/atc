import discord
from discord.ext import commands
from discord import app_commands

import random


OUTCOMES = [
    (95, ":airplane_arriving: Butter. The passengers didn't even notice."),
    (85, ":airplane_arriving: Smooth landing."),
    (70, ":airplane_arriving: Nice landing. Coffee survived."),
    (55, ":airplane_arriving: Firm arrival. Maintenance is taking notes."),
    (40, ":airplane_arriving: You definitely landed."),
    (25, ":airplane_arriving: The runway felt that one."),
    (10, ":airplane_arriving: The cabin is filing complaints."),
    (0,  ":boom: Crash landing. Fire crews responding."),
]

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="members", description="Server member count.")
    async def members(self, interaction: discord.Interaction):

        guild = interaction.guild
        humans = sum(not m.bot for m in guild.members)
        bots = len(guild.members) - humans
        
        await interaction.response.send_message(
            f":busts_in_silhouette: {humans} + :robot: {bots}"
        )

    @app_commands.command(name="landing", description="Attempt a landing.")
    async def landing(self, interaction: discord.Interaction):
        butter = max(0, min(100, int(random.gauss(72, 22))))
        vs = -int(30 + (100 - butter) * 17 + random.randint(-40, 40))
        crosswind = random.randint(0, 35)
        bounce = min(3, max(0, (100 - butter) // 30 + random.randint(0, 1)))

        for threshold, text in OUTCOMES:
            if butter >= threshold:
                outcome = text
                break

        await interaction.response.send_message(
            f"`LANDING REPORT`\n"
            f"Vertical Speed {vs:,} ft/min, "
            f"Crosswind {crosswind} kt, "
            f"and {bounce} {'bounce' if bounce == 1 else 'bounces'}.\n"
            f"**Score:** {butter}/100\n\n"
            f"{outcome}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
