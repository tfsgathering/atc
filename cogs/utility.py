import discord
from discord.ext import commands
from discord import app_commands
import aiohttp


TO = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    ' ': '/'
}

FROM = {v: k for k, v in TO.items()}


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # METAR
    @app_commands.command(name="metar", description="Get METAR for an airport")
    async def metar(self, interaction: discord.Interaction, icao: str):
        icao = icao.upper()

        url = f"https://api.checkwx.com/metar/{icao}/decoded"
        headers = {"X-API-Key": self.bot.apixkey}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await interaction.response.send_message("Could not fetch data.", ephemeral=True)
                    return
                data = await resp.json()

        if not data.get("data"):
            await interaction.response.send_message(f"No METAR found for `{icao}`.", ephemeral=True)
            return

        metar = data["data"][0]

        station = metar.get("station", {}).get("name", icao)
        time = metar.get("observed", "Unknown")
        wind = metar.get("wind", {})
        temp = metar.get("temperature", {}).get("celsius", "N/A")
        dew = metar.get("dewpoint", {}).get("celsius", "N/A")
        pressure = metar.get("barometer", {}).get("hpa", "N/A")
        vis = metar.get("visibility", {}).get("meters", "N/A")

        wind_dir = wind.get("degrees", "Calm")
        wind_speed = wind.get("speed_kts", 0)

        msg = (
            f"**{station}** (`{icao}`)\n"
            f"Time: {time}\n"
            f"Wind: {wind_dir}° at {wind_speed} kt\n"
            f"Visibility: {vis} m\n"
            f"Temp: {temp}°C | Dew: {dew}°C\n"
            f"Pressure: {pressure} hPa"
        )

        await interaction.response.send_message(msg)

    @app_commands.command(name="morsify", description="Convert text to Morse code")
    async def morsify(self, interaction: discord.Interaction, text: str):
        text = " ".join(text.split()).upper()

        result = [TO[c] for c in text if c in TO]

        if not result:
            await interaction.response.send_message("Invalid input.", ephemeral=True)
            return

        await interaction.response.send_message(" ".join(result))

    @app_commands.command(name="translate", description="Convert Morse to English")
    async def translate(self, interaction: discord.Interaction, code: str):
        code = code.replace("—", "-").replace("–", "-").replace("_", "-")

        words = code.split("/")
        decoded_words = []

        for word in words:
            letters = word.strip().split()
            decoded = "".join(FROM.get(l, "?") for l in letters)
            decoded_words.append(decoded)

        result = " ".join(decoded_words)

        await interaction.response.send_message(result, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
