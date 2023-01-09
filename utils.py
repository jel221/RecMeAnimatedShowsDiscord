import requests
import json
import discord
import urllib.parse

UNEXPECTED_ERROR = discord.Embed(
                title="Unexpected Error",
                description="Please try again.",
                color=0xE02B2B
            )

QUERY_ERROR = discord.Embed(
                title="No results found.",
                description="Please use the full romaji name of the show (e.g. Instead of 'AOT', try 'Shingeki no Kyojin'.",
                color=0xE02B2B
            )     

ARG_ERROR = discord.Embed(
                title="Incorrect argument",
                description="Rating should be a whole number from 1 to 10.",
                color=0xE02B2B
            )    

def get_embed(show : dict):
    embed = discord.Embed(
        title = show["title"],
        description = show["synopsis"],
    )
    embed.set_image(url=show["images"]["jpg"]["image_url"])
    return embed

def get_id_embed(id):
    link = f"https://api.jikan.moe/v4/anime/{id}"
    data = requests.get(link)
    show = json.loads(data.text)["data"]
    embed = discord.Embed(
        title = show["title"]
    )
    embed.set_thumbnail(url=show["images"]["jpg"]["image_url"])
    return embed

def get_first_result(q):
    query = urllib.parse.quote(q)
    link = f"https://api.jikan.moe/v4/anime?q='{query}'"
    data = requests.get(link)
    query = json.loads(data.text)
    return query["data"][0]

def get_rand_result(genre):
    link = f"https://api.jikan.moe/v4/random/anime?genres='{genre}'"
    data = requests.get(link)
    query = json.loads(data.text)
    return query["data"]