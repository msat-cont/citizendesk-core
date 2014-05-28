#!/usr/bin/env python
#
# Citizen Desk
#
'''
POST request:

/citizendesk/tweet/%%tweet_id%%

json data:
* tweet
* feed_filter
* endpoint

POST request:

/citizendesk/tweet_users/%%user_id%%

json data:
* user
'''

import os, sys, datetime, json
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.common.holder import ReportHolder
from citizendesk.common.citizen_holder import CitizenHolder

holder = ReportHolder()
citizen_holder = CitizenHolder()

def get_conf(name):
    config = {
        'feed_type': 'tweet',
        'publisher': 'twitter',
        'authority': 'twitter'
    }

    if name in config:
        return config[name]
    return None

def gen_id(feed_type, id_str):
    try:
        id_value = '' + feed_type + ':' + id_str
        return id_value
    except:
        return None

def get_tweet(report_id):
    try:
        return holder.provide_report(get_conf('feed_type'), report_id)
    except:
        return None

twt_take = Blueprint('twt_take', __name__)
twt_user_take = Blueprint('twt_user_take', __name__)

@twt_take.route('/newstwister/tweets/<tweet_id>', defaults={}, methods=['POST'], strict_slashes=False)
def take_twt(tweet_id):
    from citizendesk.ingest.twt.process import do_post

    logger = get_logger()
    client_ip = get_client_ip()

    allowed_ips = get_allowed_ips()
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: '+ str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    try:
        json_data = request.get_json(True, False, False)
        if type(json_data) is not dict:
            json_data = None
    except:
        json_data = None
    if json_data is None:
        try:
            json_data = request.json
            if type(json_data) is not dict:
                json_data = None
        except:
            json_data = None
    if not json_data:
        logger.info('data not provided in the request')
        return ('Data not provided', 404,)
    for part in ['filter', 'tweet', 'endpoint', 'type']:
        if (part not in json_data) or (not json_data[part]):
            logger.info('No ' + str(part) + ' provided')
            return ('No ' + str(part) + ' provided', 404,)

    tweet = json_data['tweet']
    feed_filter = json_data['filter']
    endpoint = json_data['endpoint']
    channel_type = json_data['type']
    request_id = None
    if ('request' in json_data) and json_data['request']:
        request_id = json_data['request']

    try:
        res = do_post(holder, tweet_id, tweet, channel_type, endpoint, request_id, feed_filter, client_ip)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return ('tweet received\n\n', 200,)
    except Exception as exc:
        logger.warning('problem on tweet processing or saving')
        return ('problem on tweet processing or saving', 404,)

@twt_user_take.route('/newstwister/tweet_users/<user_id>', defaults={}, methods=['POST'], strict_slashes=False)
def take_twt_user(user_id):
    from citizendesk.ingest.twt.process_user import do_post as do_post_user

    logger = get_logger()
    client_ip = get_client_ip()

    allowed_ips = get_allowed_ips()
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: '+ str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    try:
        json_data = request.get_json(True, False, False)
        if type(json_data) is not dict:
            json_data = None
    except:
        json_data = None
    if json_data is None:
        try:
            json_data = request.json
            if type(json_data) is not dict:
                json_data = None
        except:
            json_data = None
    if not json_data:
        logger.info('data not provided in the request')
        return ('Data not provided', 404,)
    for part in ['user']:
        if (part not in json_data) or (not json_data[part]):
            logger.info('No ' + str(part) + ' provided')
            return ('No ' + str(part) + ' provided', 404,)

    user_info = json_data['user']

    try:
        res = do_post_user(citizen_holder, user_id, user_info, client_ip)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        message = 'user info received'
        if len(res) > 1:
            message = res[1]
        return (json.dumps(message) + '\r\n', 200,)
    except Exception as exc:
        logger.warning('problem on user info processing or saving')
        return ('problem on user info processing or saving', 404,)

