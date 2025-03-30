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
token = os.environ['TOKEN']
sink_token = os.environ['SINK_TOKEN']
sink_url = os.environ['SINK_API_URL']

## Log in as the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
    print('Logged in as a bot {0.user}'.format(bot))


@bot.hybrid_command(
    name="quote",
    description="Test Command that gives a quote",
    guild=discord.Object(id=934323409444302898)
)
async def quote(ctx, test: str):
   # from this link: https://genshin-impact.fandom.com/wiki/Kaedehara_Kazuha/Voice-Overs
   kazu_quotes = ["Come driving rain or winds that churn, I shall return, by blade alone, armed, if barefoot, to my home... I am Kaedehara Kazuha, a wanderer who roams the land. Since we are both travelers, let us journey together for a time.","The wind has ceased... The world is silent, so now is the best time to rest well. See you tomorrow."]
   await ctx.send(str(random.choice(kazu_quotes)))


@commands.is_owner()
@bot.command(name='sync-commands-global', description='Sync the commands with the database')
async def sync_commands(ctx):
    try:
        await ctx.bot.tree.sync()
        await ctx.send('Commands synced to all guilds')
    except Exception as e:
        await ctx.send(f'Error syncing commands: {e}')

@commands.is_owner()
@bot.command(name='sync-commands-local', description='Sync the commands to the current guild')
async def _sync_commands_local(ctx):
    try:
        await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send('Commands synced to the guild: ' + str(ctx.guild.id))
        synced_commands = await bot.tree.fetch_commands(guild=ctx.guild)
        for cmd in synced_commands:
            print(f'Guild Commands: {cmd.name} to guild: ' + str(ctx.guild.id))
    except Exception as e:
        await ctx.send(f'Error syncing commands: {e}')

"""
@commands.is_owner()
@client.command(name='synd-url-db', description='Sync')
"""


bot.run(token)