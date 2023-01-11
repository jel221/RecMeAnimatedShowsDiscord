import os
import json
import platform
import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands import CommandNotFound
import aiosqlite
from commands import Recommendations

# Loads config file. Needed for prefix and token.
with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
    config = json.load(file)

# Requires permission to read message content
intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned_or(config["prefix"]), intents=intents, help_command=None)
bot.config = config

@bot.event
async def on_ready() -> None:
    await bot.add_cog(Recommendations(bot))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="anime, Type {} for help".format("$ar")))
    print(f"Logged in as {bot.user}")

# Awaits for input
@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return

    await bot.process_commands(message)

# Error handler so that the bot does not crash
@bot.event
async def on_command_error(context: Context, error) -> None:
    if isinstance(error, CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Incorrect number of arguments",
            description="Type **$ar** to see all available commands and their usage \n *Hint: If a name contains spaces, enclose it in quotes!*",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    raise error

# Initializes database
async def init_db():
    async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql") as file:
            await db.executescript(file.read())
        await db.commit()


asyncio.run(init_db())
bot.run(config["token"])