"""
Sink API Request Handlers
"""


import requests
import json
import datetime
import time
import re
import database

def sink_create_link(sink_url, sink_token, link_url, comment, slug = None, expiration = None):
    # TODO - Add error processing
    endpoint_url = 'link/create'
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + sink_token
    }
    payload = {
        'url': link_url,
        'comment': comment
    }
    if not expiration is None and type(expiration) is int:
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=int(expiration))        
        payload['expiration'] = int(time.mktime(expiration_date.timetuple()))
    if not slug is None:
        payload['slug'] = slug
    payload = json.dumps(payload)
    response = requests.post(sink_url+endpoint_url, headers=headers, data=payload)

    # Exit if not succsussful
    if response.status_code != 201:
        response_info = response.json()
        return({'status':"Error", 'reason':f'Creation of link failed with http error: {response.status_code}\n' + \
            f'Here is some info that might help:\n{response_info}'})
    
    # Sync new URL to database
    db_status = database.add_link_to_db(response.json()['link'], sink_url)
    if db_status['status'] == 'Error':
        db_status['reason'] += '\n' +\
            'Link created, but not synced to DB. Please report to URL bot admins'
        return(db_status)
    
    # Parse returned link data and return it
    response = parse_link_info(response.json()['link'], sink_url)
    return({'status':'Success', 'reason': "Link Created!\n" + \
        f'**Short Link:** {response['shortLink']}\n' + \
        f'**URL:** {response['url']}\n' + \
        f'**Expiration:** {response['expiration']}\n' + \
        f'**Comment:** {response['comment']}'})


def sink_update_link():

    return(response)


def sink_delete_link(sink_url, sink_token, slug):
    endpoint_url = 'link/delete'
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + sink_token
    }
    payload = {
        'slug': slug
    }
    payload = json.dumps(payload)
    response = requests.post(sink_url+endpoint_url, headers=headers, data=payload)

    # Exit if not succsussful
    if response.status_code != 204:
        response_info = response.json()
        return({'status':"Error", 'reason':f'Creation of link failed with http error: {response.status_code}\n' + \
            f'Here is some info that might help:\n{response_info}'})
    
    # Delete from database
    db_status = database.delete_link('slug',slug)
    if db_status['status'] == 'Error':
        db_status['reason'] += '\n' +\
            'Link deleted, but not synced to DB. Please report to URL bot admins'
        return(db_status)
    
    # Everything should be good, let's dip
    return({'status':'Success', 'reason': f'Link with slug: `{slug}` deleted!'})


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


def parse_link_info(link_info_dict, sink_url):
    """Accepts the link info json/dict and returns a more human-friendly dictionary"""
    response = {}
    if 'expiration' in link_info_dict:
        expiration = datetime.datetime.fromtimestamp(link_info_dict['expiration'])
        expiration = expiration.strftime('%m-%d-%Y')
        response['expiration'] = expiration
    else:
        response['expiration'] = "No Expiration"
    response['url'] = link_info_dict['url']
    comment_json = json.loads(link_info_dict['comment'])
    response['comment'] = comment_json['comment']
    response['shortLink'] = re.search(r"https\:\/\/.*?\.\w+", sink_url).group() + '/' + link_info_dict['slug']
    return(response)
    


    