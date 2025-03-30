"""
Sink API Request Handlers
"""


import requests
import json
import datetime
import time

def sink_create_link(sink_url, sink_token, link_url, comment, expiration, slug):
    endpoint_url = 'link/create'
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + sink_token
    }
    payload = {
        'url': link_url,
        'slug': slug,
        'comment': comment
    }
    if not expiration is None:
        payload['expiration'] = int(expiration)
    payload = json.dumps(payload)
    response = requests.post(sink_url+endpoint_url, headers=headers, data=payload)
    # TODO - Add error processing
    # TODO - Add DB connectors
    return(response)


def sink_update_link():

    return(response)


def sink_delete_link():

    return()


def sink_search():

    return()


def sink_generate_slug():

    return()


def sink_list_all(sink_url, sink_token, limit=None):
    endpoint_url = 'link/list'
    if not limit is None: endpoint_url += '?limit=' + str(limit)
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + sink_token
    }
    response = requests.get(sink_url+endpoint_url, headers=headers)
    # TODO - Add error processing
    return(response.json())
    