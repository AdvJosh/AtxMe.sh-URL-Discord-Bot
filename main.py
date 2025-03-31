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
import database
import api_calls
import json
import datetime
import time



## Set up client and log into Discord
# Set Up ENV Variables
load_dotenv('.env')
token = os.environ['TOKEN']
sink_token = os.environ['SINK_TOKEN']
sink_url = os.environ['SINK_API_URL']
url_admin_roles = eval(os.environ['URL_ADMIN_ROLES'])
dev_guild_id = int(os.environ['DEV_GUILD_ID'])


## Log in as the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
    print('Logged in as a bot {0.user}'.format(bot))

"""
@bot.hybrid_command(
    name="atxmesh-quote",
    description="Test Command that gives a quote",
    guild=discord.Object(id=dev_guild_id) # TODO Remove guild after testing
)
async def quote(ctx, test: str):
   # from this link: https://genshin-impact.fandom.com/wiki/Kaedehara_Kazuha/Voice-Overs
   kazu_quotes = ["Come driving rain or winds that churn, I shall return, by blade alone, armed, if barefoot, to my home... I am Kaedehara Kazuha, a wanderer who roams the land. Since we are both travelers, let us journey together for a time.","The wind has ceased... The world is silent, so now is the best time to rest well. See you tomorrow."]
   await ctx.send(str(random.choice(kazu_quotes)))
"""


## These are the sync commands
@commands.is_owner()
@bot.command(name='sync-commands-global', description='Sync the commands with the database')
async def sync_commands(ctx):
    try:
        await ctx.bot.tree.sync()
        await ctx.send('Commands synced to all guilds')
        synced_commands = await bot.tree.fetch_commands()
        print(f'Global Commands: {synced_commands}')
    except Exception as e:
        await ctx.send(f'Error syncing commands: {e}')


@commands.is_owner()
@bot.command(name='sync-commands-local', description='Sync the commands to the current guild')
async def _sync_commands_local(ctx):
    try:
        await ctx.bot.tree.sync(guild=discord.Object(id=dev_guild_id))
        await ctx.send('Commands synced to the guild: ' + str(discord.Object(id=dev_guild_id).id))
        synced_commands = await bot.tree.fetch_commands(guild=discord.Object(id=dev_guild_id))
        for cmd in synced_commands:
            print(f'Guild Commands: {cmd.name} to guild: ' + str(discord.Object(id=dev_guild_id).id))
    except Exception as e:
        await ctx.send(f'Error syncing commands: {e}')


### =-=-= START APPLICATION COMMANDS =-=-= ###

## Admin Commands ##
@bot.hybrid_command(
    name='sync-url-db', 
    description='Sync all Sink links to the local database',
    )
async def sync_url_db(ctx, member: discord.Member = None):
    member_roles = {role.id for role in ctx.author.roles}
    if member_roles & set(url_admin_roles):
        await ctx.send('Syncing the DB.... Please wait....', ephemeral=True)
        try: 
            db_sync_status = database.update_link_db(sink_url, sink_token)
            await ctx.send(db_sync_status, ephemeral=True)
        except Exception as e:
            await ctx.send(f'Error syncing database: {e}', ephemeral=True)
    else:
        await ctx.send('You do not have sufficient privilege to call this command', ephemeral=True)


@bot.hybrid_command(
    name='ban-link-user',
    description='Bans a user from using the atxme.sh bot'
)
async def ban_link_user(ctx, member: discord.Member, reason: str):
    member_roles = {role.id for role in ctx.author.roles}
    if not member_roles & set(url_admin_roles):
        await ctx.send('You do not have sufficient privilege to call this command')
        return()
    if member == ctx.author:
        await ctx.send('You cannot ban yourself.', ephemeral=True)
        return()
    
    response = database.add_user_ban(member.id, ctx.author.id, reason)
    await ctx.send(f'Banning user {member.display_name}\n' + \
        f'**Status:** {response['status']}\n' + \
        f'**Reason:** {response['reason']}', ephemeral=True)


@bot.hybrid_command(
    name='unban-link-user',
    description="Remove a user from being banned from the atxme.sh bot"
)
async def unban_link_user(ctx, member: discord.Member):
    member_roles = {role.id for role in ctx.author.roles}
    if not member_roles & set(url_admin_roles):
        await ctx.send('You do not have sufficient privilege to call this command')
        return()
    
    response = database.remove_user_ban(member.id)
    await ctx.send(f'Unbanning user {member.display_name}\n' + \
        f'**Status:** {response['status']}\n' + \
        f'**Reason:** {response['reason']}', ephemeral=True)


## Regular Commands ##

@bot.hybrid_command(
    name="create-link",
    description="Create a short link. Only URL is required.",
)
async def create_link(ctx, \
    url: str, \
    comment: str = None, \
    slug: str = None, \
    expiration: int = None):
    is_admin = False

    # Default ban checker
    ban_check = database.check_ban_status(ctx.author.id)
    if type(ban_check) is list:
        try:
            banned_by = await ctx.guild.fetch_member(ban_check[2])
            banned_by = banned_by.display_name
        except Exception as e:
            banned_by = ban_check[2]
            print(f"Failed to fetch banned by user with error {e}")
        await ctx.send('You have been banned from the url bot.\n' + \
            f'**Banned By:** {banned_by}\n' + \
            f'**Ban Reason:** {ban_check[3]}\n' + \
            'Please reach out to the bot admins if you feel this is in error', \
            ephemeral=True)
        return()

    # Check if they are admin
    member_roles = {role.id for role in ctx.author.roles}
    if member_roles & set(url_admin_roles):
        is_admin = True
    
    # Check if slug exists in DB, stop if it does
    if not slug is None:
        response = database.check_slug_exists(slug)
        if response['status'] == 'Error':
            await ctx.send(f'Error when creating short link.\n Error Message:\n```{response['reason']}```', \
                ephemeral= True)
            return()

    # Build comment string
    comment_str = {'userID': ctx.author.id}
    if comment is None: comment_str['comment'] = ""
    else: comment_str['comment'] = comment
    comment_str = json.dumps(comment_str)

    # Set expirtation date based on permissions
    if expiration is None: expiration = 30
    elif expiration == 0 and is_admin: expiration = None
    elif expiration == 0: expiration = 30
    elif expiration > 30 and is_admin: expiration = expiration
    elif expiration > 30: expiration = 30

    # Try and create the short link
    response = api_calls.sink_create_link(sink_url, sink_token, url, comment_str, slug, expiration)
    if response['status'] == 'Success':
        await ctx.send(f'Short link created!\n {response['reason']}', ephemeral=True)
    elif response['status'] == 'Error':
        await ctx.send(f'Error creating short link.\nError Message:\n```{response['reason']}```', ephemeral=True)
    else:
        await ctx.send('An unknown error occurred when creating the link', ephemeral=True)


@bot.hybrid_command(
    name='list-short-links',
    description='Get a list of all your short links'
)
async def list_user_short_links(ctx, member:discord.Member = None):
    is_admin = False

    # Default ban checker
    ban_check = database.check_ban_status(ctx.author.id)
    if type(ban_check) is list:
        try:
            banned_by = await ctx.guild.fetch_member(ban_check[2])
            banned_by = banned_by.display_name
        except Exception as e:
            banned_by = ban_check[2]
            print(f"Failed to fetch banned by user with error {e}")
        await ctx.send('You have been banned from the url bot.\n' + \
            f'**Banned By:** {banned_by}\n' + \
            f'**Ban Reason:** {ban_check[3]}\n' + \
            'Please reach out to the bot admins if you feel this is in error', \
            ephemeral=True)
        return()

    # Check if they are admin
    member_roles = {role.id for role in ctx.author.roles}
    if member_roles & set(url_admin_roles):
        is_admin = True
    
    # If not admin, tell them they cant get others URLs
    if is_admin == False and not member is None:
        await ctx.send('You don\'t have sufficient permission to get other peoples\' urls', ephemeral=True)
        return()
    
    # If member is none, get their urls
    if member is None:
        response = database.get_users_links(ctx.author.id)
        if response['status'] == 'Error':
            await ctx.send(f'Error fetching URLs.\nError Message: ```{response['reason']}```', ephemeral=True)
            return()
        msg = url_db_to_msg(response['payload'])
        await ctx.send(f'Here are your short links:\n{msg}', ephemeral=True)

    # If admin and members != none, get their urls
    if is_admin and not member is None:
        response = database.get_users_links(member.id)
        if response['status'] == 'Error':
            await ctx.send(f'Error fetching URLs.\nError Message: ```{response['reason']}```', ephemeral=True)
            return()
        msg = url_db_to_msg(response['payload'])
        await ctx.send(f'Here are the short links for {member.display_name}:\n{msg}', ephemeral=True)


@bot.hybrid_command(
    name='delete-link',
    description='Delete a short link. Requires slug - can be used to recreate link'
)
async def delete_link(ctx, slug: str):
    is_admin = False

    # Default ban checker
    ban_check = database.check_ban_status(ctx.author.id)
    if type(ban_check) is list:
        try:
            banned_by = await ctx.guild.fetch_member(ban_check[2])
            banned_by = banned_by.display_name
        except Exception as e:
            banned_by = ban_check[2]
            print(f"Failed to fetch banned by user with error {e}")
        await ctx.send('You have been banned from the url bot.\n' + \
            f'**Banned By:** {banned_by}\n' + \
            f'**Ban Reason:** {ban_check[3]}\n' + \
            'Please reach out to the bot admins if you feel this is in error', \
            ephemeral=True)
        return()

    # Check if they are admin
    member_roles = {role.id for role in ctx.author.roles}
    if member_roles & set(url_admin_roles):
        is_admin = True
    
    # Get creator of short link
    response = database.get_link_creator('slug',slug)
    if response['status'] == 'Error':
        await ctx.send(f'Couldn\'t get the creator information for the link you provided. Error Message: ' + \
            f'```{response['reason']}```', ephemeral=True)
        return()
    else:
        creator_id = response['payload']
    
    # If not admin, tell them they can't delete others URLs
    if is_admin == False and creator_id != ctx.author.id:
        await ctx.send('You don\'t have sufficient permission to delete other peoples\' urls', ephemeral=True)
        return()
    
    # Else, delete that thing
    response = api_calls.sink_delete_link(sink_url, sink_token, slug)
    if response['status'] == 'Success':
        await ctx.send(f'Successfully deleted link with the slug: `{slug}`', ephemeral=True)
    elif response['status'] == 'Error':
        await ctx.send(f'Error deleting link with the slug: `{slug}`\n Error Message: '+ \
            f'```{response['reason']}```', ephemeral=True)



## Non-discord functions ##
def url_db_to_msg(url_tuple_list):
    msg_str = ""
    for index, url_tuple in enumerate(url_tuple_list):
        url_str_line = f'{index + 1}. '
        url_str_line += f'URL: `{url_tuple[3]}`\n '
        url_str_line += f'Slug: `{url_tuple[4]}`\n '
        url_str_line += f'Short Link: `{url_tuple[2]}`\n '
        if url_tuple[6] is None:
            url_str_line += f'Expires: `Never`'
        else:
            print(f'Expiration is: {url_tuple[6]}')
            print(f'Expiration type is {type(url_tuple[6])}')
            expiration = datetime.datetime.fromtimestamp(url_tuple[6])
            expiration = expiration.strftime('%m-%d-%Y')
            url_str_line += f'Expires: `{expiration}`'
        url_str_line += '\n'
        msg_str += url_str_line
    return(msg_str)


bot.run(token)