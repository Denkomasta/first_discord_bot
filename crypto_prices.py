import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

# Create bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='@', intents=intents)

# Command to fetch cryptocurrency price
@bot.command(name='price')
async def crypto_price(ctx, symbol: str):
    """
    Fetches the current price of a cryptocurrency by symbol.
    Example: !price BTC
    """
    try:
        # Fetch data from a cryptocurrency API
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd")
        data = response.json()

        # Check if data is valid
        if symbol.lower() in data:
            price = data[symbol.lower()]["usd"]
            await ctx.send(f"The current price of **{symbol.upper()}** is **${price:.2f}** USD.")
        else:
            await ctx.send(f"Could not find price data for **{symbol.upper()}**. Please check the symbol.")
    except Exception as e:
        await ctx.send("An error occurred while fetching the price. Please try again later.")
        print(f"Error: {e}")

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)