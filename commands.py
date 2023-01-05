import os
import random

import discord
from discord.ext import commands
import aiosqlite
from utils import *

class Recommendations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ar(self, ctx):
        embed = discord.Embed(
                title="Usage",
                description="""
                Usage:
                
                **$rec [Optional: Number of recommendations (Max 5)]** to be recommended a show based on your ratings.

                **$rand [Genre]** to be recommended a random show within a genre.

                **$showadd [Show Name] [Rating (1 for worst, 10 for best)]** to add/change a show to your list of watched shows.

                **$showrm [Show Name]** to remove a show from your list of watched shows.

                **$showinfo [Show Name]** to find information on a show.
                """,
                color=0x7289DA
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def rec(self, ctx, arg = 1):
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


    @commands.command()
    async def rand(self, ctx, genre=""):
        try:
            show = get_rand_result(genre)
        except:
            await ctx.send(embed=UNEXPECTED_ERROR)
            return
        
        embed = get_embed(show)
        await ctx.send(embed=embed)
        

    @commands.command()
    async def showadd(self, ctx, q, rat):
        try:
            rating = int(rat)
            assert 1 <= rating <= 10
        except:
            bad_arg = discord.Embed(
                title="Incorrect argument",
                description="Rating should be a whole number from 1 to 10.",
                color=0xE02B2B
            )
            await ctx.send(embed=bad_arg)
            return

        try:
            top_result = get_first_result(q)
        except NoResultException as _:
            await ctx.send(embed=QUERY_ERROR)
            return
        except Exception as _:
            await ctx.send(embed=UNEXPECTED_ERROR)
        
        show_name = top_result["title"]
        show_id = top_result["mal_id"]
        uid = ctx.author.id

        async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
            await db.execute("DELETE FROM likes WHERE id = {id} AND idx = {idx}".format(id=uid, idx=show_id))
            await db.execute("INSERT INTO likes VALUES({id}, {idx}, {rat})".format(id=uid, idx=show_id, rat=rating))
            await db.commit()
        
        embed = discord.Embed(
                title="Added",
                description= f"**{show_name}** has been added to your list of watched shows.",
                color=0x1ABC9C
            )
        await ctx.send(embed=embed)
        

    @commands.command()
    async def showrm(self, ctx, q):
        try:
            top_result = get_first_result(q)
        except NoResultException as _:
            await ctx.send(embed=QUERY_ERROR)
            return
        except Exception as _:
            await ctx.send(embed=UNEXPECTED_ERROR)

        show_name = top_result["title"]
        show_id = top_result["mal_id"]
        uid = ctx.author.id

        async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
            await db.execute("DELETE FROM likes WHERE id = {id} AND idx = {idx}".format(id = uid, idx=show_id))
            await db.commit()
        
        embed = discord.Embed(
                title="Removed",
                description= f"**{show_name}** has been removed from your list of watched shows.",
                color=0x1ABC9C
            )
        await ctx.send(embed=embed)


    @commands.command()
    async def showinfo(self, ctx, q):
        show = get_first_result(q)
        embed = self.get_embed(show)
        await ctx.send(embed=embed)

