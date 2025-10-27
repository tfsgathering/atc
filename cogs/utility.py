import discord
from discord.ext import commands
import aiohttp


class Utility(commands.Cog):
    """Utility commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def metar(self, ctx, icao: str):
        """Returns Meteorological Aerodrome Report of the given airport."""
        
        icao = icao.upper()
        url = f"https://api.checkwx.com/metar/{icao}/decoded"
        headers = {"X-API-Key": self.bot.xapikey}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await ctx.send(":cross: Could not fetch data.")
                    return
                data = await resp.json()

        if not data.get("data"):
            await ctx.send(f":warning: No METAR found for `{icao}`.")
            return

        metar = data["data"][0]
        station = metar.get("station", {}).get("name", icao)
        time = metar.get("observed", "Unknown time")
        wind = metar.get("wind", {})
        temp = metar.get("temperature", {}).get("celsius", "N/A")
        dew = metar.get("dewpoint", {}).get("celsius", "N/A")
        pressure = metar.get("barometer", {}).get("hpa", "N/A")
        vis = metar.get("visibility", {}).get("meters", "N/A")

        wind_dir = wind.get("degrees", "Calm")
        wind_speed = wind.get("speed_kts", 0)

        msg = (
            f"METAR for `{icao}`: **{station}**\n"
            f"Time: {time}\n"
            f"Wind: {wind_dir} deg at {wind_speed} kt\n"
            f"Visibility: {vis} m\n"
            f"Temp.: {temp} deg C | Dew: {dew}°C\n"
            f"Pressure: {pressure} hPa"
        )

        await ctx.send(msg)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
