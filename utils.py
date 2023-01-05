import requests
import json
import discord

class NoResultException(Exception):
    "Raised when no results are found from the query."
    pass

UNEXPECTED_ERROR = discord.Embed(
                title="Unexpected Error",
                description="Please try again.",
                color=0xE02B2B
            )

QUERY_ERROR = discord.Embed(
                title="No results found.",
                description="Please check for any errors in the name.",
                color=0xE02B2B
            )            

def get_embed(show : dict):
    embed = discord.Embed(
        title = show["title"],
        description = show["synopsis"],
    )
    embed.set_image(url=show["images"]["jpg"]["image_url"])
    return embed

def get_first_result(q):
    link = f"https://api.jikan.moe/v4/anime?q='{q}"
    data = requests.get(link)
    query = json.loads(data.text)
    if query["items"]["count"] == 0:
        raise NoResultException
    return query["data"][0]

def get_rand_result():
    link = f"https://api.jikan.moe/v4/anime?q='{q}"
    data = requests.get(link)
    query = json.loads(data.text)
    return query["data"]