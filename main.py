import os
import sys
import json
import platform
import asyncio
import random
import re

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands import CommandNotFound
import aiosqlite
from AnilistPython import Anilist

with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
    config = json.load(file)

intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned_or(config["prefix"]), intents=intents, help_command=None)
bot.config = config

anilist = Anilist()

@bot.event
async def on_ready() -> None:
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="anime, Type {} for help".format("$ar")))
    print(f"Logged in as {bot.user}")
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return

    await bot.process_commands(message)


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


@bot.command()
async def ar(ctx):
    embed = discord.Embed(
            title="Usage",
            description="""
            Usage:
            
            **$rec [Optional: Number of recommendations (Max: 5)]** to be recommended a show based on your ratings.

            **$rand [Genre]** to be recommended a random show within a genre.

            **$showadd [Show Name] [Rating (1 for worst, 10 for best)]** to add/change a show to your list of watched shows.

            **$showrm [Show Name]** to remove a show from your list of watched shows.

            **$showinfo [Show Name]** to find information on a show.
            """,
            color=0x7289DA
    )
    await ctx.send(embed=embed)


@bot.command()
async def rec(ctx, arg = 1):
    if not isinstance(arg, int) or not 1 <= arg <= 5:
        embed = discord.Embed(
            title="Incorrect argument",
            description="Rating should be a whole number from 1 to 5.",
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    uid = ctx.author.id
    async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
        rows = await db.execute_fetchall("SELECT id, idx, value FROM likes WHERE id = {id}".format(id=uid))
    for r in rows:
        print(r)
    # ML ALGORITHM


@bot.command()
async def rand(ctx, arg):
    genre_list = anilist.search_anime(genre=arg)
    show = random.choice(genre_list)
    embed = get_embed(show)
    await ctx.send(embed=embed)
    

@bot.command()
async def showadd(ctx, arg1, arg2):
    embed = discord.Embed(
            title="Incorrect argument",
            description="Rating should be a whole number from 1 to 10.",
            color=0xE02B2B
        )
    try:
        arg2 = int(arg2)
    except:
        await ctx.send(embed=embed)
        return
    if not (1 <= arg2 <= 10):
        await ctx.send(embed=embed)
        return
    uid = ctx.author.id
    show_name = str(arg1)
    show_id = anilist.get_anime_id(show_name)
    rating = arg2

    async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
        await db.execute("DELETE FROM likes WHERE id = {id} AND idx = {idx}".format(id=uid, idx=show_id))
        await db.execute("INSERT INTO likes VALUES({id}, {idx}, {rat})".format(id=uid, idx=show_id, rat=rating))
        await db.commit()
    

@bot.command()
async def showrm(ctx, arg):
    uid = ctx.author.id
    show_id = anilist.get_anime_id(arg)
    async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
        await db.execute("DELETE FROM likes WHERE id = {id} AND idx = {idx}".format(id = uid, idx=show_id))
        await db.commit()

@bot.command()
async def showinfo(ctx, arg):
    show = anilist.get_anime(arg)
    embed = get_embed(show)
    await ctx.send(embed=embed)


def get_embed(show : dict):
    CLEANR = re.compile('<.*?>') 
    cleantext = re.sub(CLEANR, '', show["desc"])
    embed = discord.Embed(
        title = show["name_romaji"],
        description = cleantext,
    )
    embed.set_image(url=show["cover_image"])
    return embed


async def init_db():
    async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql") as file:
            await db.executescript(file.read())
        await db.commit()


asyncio.run(init_db())
bot.run(config["token"])