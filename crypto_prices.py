import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
import asyncio
import signal
import sys
from database import Database

Data: Database = Database()

# Loads private discord bot token from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
CMD_PREFIX = '-'
if not token:
    raise ValueError("DISCORD_TOKEN not found in .env file!")

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)

# Event: On bot ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# ctx == discord context
# command hello
@bot.command(name='hello', help='Replies with Hello!')
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author}!')

# Command to fetch cryptocurrency price - command price
@bot.command(name='price', help='Replies with current price of written symbol of cryptocurrency')
async def crypto_price(ctx, symbol: str):
    """
    Fetches the current price of a cryptocurrency by symbol.
    Example: !price BTC
    """
    try:
        # Fetch data from a cryptocurrency API
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd")
        data = response.json()

        if symbol.lower() in data:
            price = data[symbol.lower()]["usd"]
            await ctx.send(f"The current price of **{symbol.upper()}** is **${price:.2f}** USD.")
        else:
            await ctx.send(f"Could not find price data for **{symbol.upper()}**. Please check the symbol.")
    except Exception as e:
        await ctx.send("An error occurred while fetching the price. Please try again later.")
        print(f"Error: {e}")

@bot.command(name='register', help='Register yourself to be able to use me.')
async def register(ctx):
    user_id = ctx.author.id
    if Data.is_registered(user_id):
        await ctx.send(f"{ctx.author.mention}, you are already registered! ✅")
        return

    Data.register(user_id)
    await ctx.send(f"{ctx.author.mention}, you have been successfully registered! 🎉\n Type {CMD_PREFIX}help for more info.")

@bot.command(name='p', help='Command to work with your portfolio.')
async def portfolio(ctx):
    portfolio = Data.get_portfolio(ctx.author.id)

    if not portfolio:
        await ctx.send(f"{ctx.author.mention}, your portfolio is empty.")
        return

    portfolio_summary = f"**{ctx.author.name}'s Portfolio:**\n"
    p_s, total_value = Data.get_portfolio_summary(ctx.author.id)
    portfolio_summary = portfolio_summary + p_s
    portfolio_summary += f"**Total Portfolio Value**: ${total_value:.2f}"

    await ctx.send(portfolio_summary)

@bot.command(name='p_add', help=f'Add new cryptocurrency to your portfolio ({CMD_PREFIX}p_add [currency] [amount] [buy_price])!')
async def p_add(ctx, currency: str = None, amount: str = None, buy_price: str = None):
    sender = ctx.author
    if currency is None or amount is None or buy_price is None:
        await ctx.send(f'{sender.mention}, please specify currency amount buy_price like: `{CMD_PREFIX}p_add bitcoin 2 65000`')
        return
    
    try:
        amount = float(amount)
    except ValueError:
        await ctx.send(f'{sender.mention}, the amount must be a valid number.')
        return

    try:
        price = float(buy_price)
    except ValueError:
        await ctx.send(f'{sender.mention}, the buy_price must be a valid number.')
        return

    if Data.add_cryptocurrency(sender.id, currency, amount, price):
        await ctx.send(f'{currency.upper()} added to your portfolio.')
        return
    await ctx.send(f'{sender.mention}, the currency must be a valid crypto symbol.')

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.content.startswith(CMD_PREFIX):
        return

    if not Data.is_registered(message.author.id) and not message.content.startswith(f'{CMD_PREFIX}register'):
        await message.channel.send(
            f'{message.author.mention}, you are not registered! Use `{CMD_PREFIX}register` to start or contact an admin for assistance.'
        )
        return

    await bot.process_commands(message)

@bot.event
async def on_close():
    Data.save_portfolios()
    print("Bot disconnected, stats saved.")

def signal_handler(signal, frame):
    print("Gracefully shutting down...")
    Data.save_portfolios()
    asyncio.create_task(bot.close())
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def start_bot():
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(start_bot())