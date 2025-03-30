"""
ATxMe.sh URL Shortener Discord Bot
Created for the Austin Mesh community
By: AdvJosh
"""

import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv



## Set up client and log into Discord
# Set Up ENV Variables
load_dotenv()
token = os.getenv('TOKEN')
sink_token = os.getenv('SINK_TOKEN')
sink_url = os.getenv('SINK_API_URL')


intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)
@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))


@client.command(aliases=['quote', 'q', 'wind'])
async def _quote(ctx, test):
   # from this link: https://genshin-impact.fandom.com/wiki/Kaedehara_Kazuha/Voice-Overs
   kazu_quotes = ["Come driving rain or winds that churn, I shall return, by blade alone, armed, if barefoot, to my home... I am Kaedehara Kazuha, a wanderer who roams the land. Since we are both travelers, let us journey together for a time.","The wind has ceased... The world is silent, so now is the best time to rest well. See you tomorrow."]
   await ctx.send(str(random.choice(kazu_quotes)))


@commands.is_owner()
@client.command(name="sync-commands", description="Sync the commands with the database")
async def sync_commands(ctx: commands.Context):
    try:
        await ctx.bot.tree.sync()
        await ctx.send("Commands synced to all guilds")
    except Exception as e:
        await ctx.send(f"Error syncing commands: {e}")


client.run(token)