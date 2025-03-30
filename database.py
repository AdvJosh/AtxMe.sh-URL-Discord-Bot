"""
Handles all the database commands and connections
"""


import sqlite3
import datetime
import time
import json
import re
from api_calls import sink_list_all


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
    response = sink_list_all(sink_url, sink_token)
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
    return()
