"""
Handles all the database commands and connections
"""


import sqlite3
import datetime
import time
import json
import re
import api_calls


def create_tuple_link_data(link, sink_url):
    link_data = []
    link_data.append(link['id'])
    link_data.append(json.loads(link['comment'])['userID']) 
    link_data.append(re.search(r"https\:\/\/.*?\.\w+", sink_url).group() + '/' + link['slug'])
    link_data.append(link['url'])
    link_data.append(link['slug'])
    link_data.append(json.loads(link['comment'])['comment'])
    if 'expiration' in link:
        link_data.append(link['expiration'])
    else: link_data.append(None)
    link_data.append(link['createdAt'])
    link_data.append(link['updatedAt'])
    return(tuple(link_data))


def update_link_db(sink_url, sink_token):
    response = api_calls.sink_list_all(sink_url, sink_token)
    conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
    # Not sure if it is best to delete everything and rebuild, but it makes sense to me
    cursor.execute('DELETE FROM urls')
    conn.commit();conn.close()
    # Let's build a list of tuples of all the values
    values = []
    for link in response['links']:
        values.append(create_tuple_link_data(link, sink_url))
    conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
    cursor.executemany("INSERT INTO urls" \
        " (id, creator_discordID, short_link, url, slug, comment, expires_date, created_date, updated_date) " \
        " VALUES (?,?,?,?,?,?,?,?,?)", values)
    conn.commit();conn.close()
    return_status = str(len(values)) + " URLs have been synced to the database."
    return(return_status)


def check_ban_status(discordID):
    conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
    response = cursor.execute("SELECT * FROM banned_users WHERE discordID = ? LIMIT 1", (int(discordID),))
    response = response.fetchone()
    conn.commit();conn.close()
    if response is None:
        return(response)
    else:
        return(list(response))


def add_user_ban(discordID, banned_by, banned_reason):
    conn = None
    try:
        ban_check = check_ban_status(discordID)
        if type(ban_check) is list:
            return({'status':'Error', 'reason':f'User already banned by {ban_check[2]}. Reason: {ban_check[3]}'})
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        cursor.execute('INSERT INTO banned_users (discordID, BannedBy, BannedReason) VALUES (?,?,?);', \
            (discordID, banned_by, banned_reason))
        conn.commit();conn.close()
        ban_check = check_ban_status(discordID)
        if type(ban_check) is list:
            return({'status':'Success', 'reason':'User successfully banned from the bot and added to the DB'})
        else:
            return({'status':'Error', 'reason':'We attempted to ban the user, but it did not sync to the DB'})
    except Exception as e:
        if not conn is None: conn.close()
        return({'status':'Error', 'reason':f'{e}'})


def remove_user_ban(discordID):
    conn = None
    try:
        ban_check = check_ban_status(discordID)
        if ban_check is None:
            return({'status':'Error', 'reason':'The selected user is not on the ban list.'})
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        cursor.execute('DELETE FROM banned_users WHERE discordID = ?', (discordID,))
        conn.commit(); conn.close()
        ban_check = check_ban_status(discordID)
        if type(ban_check) is list:
            return({'status':'Error', 'reason':'We attempted to ban the user, but it did not sync to the DB'})
        elif ban_check is None:
            return({'status':'Success', 'reason':'User succsessfully unbanned'})
        else:
            return({'status':'Error', 'reason':'Something went wrong...'})
    except Exception as e:
        if not conn is None: conn.close()
        return({'status':'Error', 'reason':f'{e}'})


def add_link_to_db(link_info_dict, sink_url):
    try:
        link_info_tuple = create_tuple_link_data(link_info_dict, sink_url)
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        cursor.execute("INSERT INTO urls" \
        " (id, creator_discordID, short_link, url, slug, comment, expires_date, created_date, updated_date) " \
        " VALUES (?,?,?,?,?,?,?,?,?)", link_info_tuple)
        conn.commit(); conn.close
        return({'status':'Success', 'reason':'Link added to database'})
    except Exception as e:
        return({'status':'Error', 'reason':f'Couldn\'t sync to DB: {e}'})


def check_slug_exists(slug):
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        response = cursor.execute('SELECT * FROM urls WHERE slug = ?', (slug,))
        response = response.fetchone()
        conn.commit(); conn.close()
        if response is None:
            return({'status':'Success', 'reason':'slug is available'})
        elif type(response) is tuple:
            return({'status':'Error', 'reason':'Slug is already in use! Try a different slug,' + \
                'or leave blank for the system to generate one for you'})
        else:
            return({'status':'error', 'reason':'Unexpected condition when checking if slug exists.'})
    except Exception as e:
        if not conn is None: conn.close()
        return({'status':'Error', 'reason':f'Couldn\'t check slug in DB: {e}'})


def get_users_links(discordID):
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        response = cursor.execute('SELECT * from urls WHERE creator_discordID = ?' , (discordID,))
        response = response.fetchall()
        conn.commit(); conn.close()
        if len(response) == 0:
            return({'status':'Error', 'reason':'No urls found for user'})
        elif type(response) is list:
            return({'status':'Success', 'reason':'URL list in payload', 'payload':response})
        else:
            return({'status':'error', 'reason':'Unexpected condition when getting user URLs'})
    except Exception as e:
        if not conn is None: conn.close()
        return({'status':'Error', 'reason':f'Couldn\'t get user URLs: {e}'})

def delete_link(delete_column, value):
    # TODO add check to see if it was actually deleted
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        cursor.execute(f'DELETE FROM urls WHERE {delete_column} = ?;', (value,))
        conn.commit(); conn.close()
        return({'status':'Success', 'reason':'URL deleted from DB'})
    except Exception as e:
        if not conn is None: conn.close()
        return({'status':'Error', 'reason':f'Couldn\'t delete URL: {e}'})


def get_link_creator(search_column, value):
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite');cursor = conn.cursor()
        response = cursor.execute(f'SELECT creator_discordID FROM urls where {search_column} = ?;', (value,))
        response = response.fetchone()
        conn.commit(); conn.close()
        if response is None:
            return({'status':'Error', 'reason':f'No urls found with value {value} in column {search_column}'})
        else:
            return({'status':'Success', 'reason':'Got creator ID', 'payload': response[0]})
    except Exception as e:
        if not conn is None: conn.close()
        return({'status':'Error', 'reason':f'Couldn\'t get link creator: {e}'})
