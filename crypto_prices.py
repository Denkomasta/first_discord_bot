import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

# Loads private discord bot token from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

# Event: On bot ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# ctx == discord context
# command hello
@bot.command(name='hello', help='Replies with Hello!')
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author}!')

# ping command
@bot.command(name='ping')
async def ping(ctx):
    print("Ping command was triggered!")
    await ctx.send("Pong!")

# Command to fetch cryptocurrency price - command price
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print("Got message")
    print(message)
    await bot.process_commands(message)

bot.run(token)  #token from .env file