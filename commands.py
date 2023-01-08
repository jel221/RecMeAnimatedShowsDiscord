import os
import discord
from discord.ext import commands
import aiosqlite
from utils import *
import training.model as model

class Recommendations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = model.Model()

    @commands.command()
    async def ar(self, ctx):
        embed = discord.Embed(
                title="Usage",
                description="""
                Usage:
                
                **$rec [Optional: Number of recommendations (Max 10)]** to be recommended a show based on your ratings.

                **$rand [Genre]** to be recommended a random show within a genre.

                **$showadd [Show Name] [Rating (1 for worst, 10 for best)]** to add/change a show to your list of watched shows.

                **$showrm [Show Name]** to remove a show from your list of watched shows.

                **$showinfo [Show Name]** to find information on a show.
                *Hint:* Please use the full romaji name of the show (e.g. Instead of 'Attack on Titan' or 'AoT', try 'Shingeki no Kyojin'.
                """,
                color=0x7289DA
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def rec(self, ctx, num = 1):
        if not isinstance(num, int) or not 1 <= num <= 10:
            await ctx.send(embed=ARG_ERROR)
        uid = ctx.author.id
        async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
            rows = await db.execute_fetchall("SELECT idx, value FROM likes WHERE id = {id}".format(id=uid))
        result = self.model.get_result(rows, num)
        for i in range(num):
            embed = get_id_embed(result[i])
            await ctx.send(f"Recommendation #{i}", embed=embed)


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
            print(q)
            print(rat)
            rating = int(rat)
            assert (rating >= 1 and rating <= 10)
        except:
            await ctx.send(embed=ARG_ERROR)
            return

        try:
            top_result = get_first_result(q)
        except IndexError:
            await ctx.send(embed=QUERY_ERROR)
            return
        except Exception:
            await ctx.send(embed=UNEXPECTED_ERROR)
            return
        
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
        except IndexError:
            await ctx.send(embed=QUERY_ERROR)
            return
        except Exception:
            await ctx.send(embed=UNEXPECTED_ERROR)
            return

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
        try:
            show = get_first_result(q)
        except IndexError:
            await ctx.send(embed=QUERY_ERROR)
            return
        except Exception:
            await ctx.send(embed=UNEXPECTED_ERROR)
            return

        embed = get_embed(show)
        await ctx.send(embed=embed)

