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

'''

import os, sys, datetime, json
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.reporting.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.reporting.holder import ReportHolder

holder = ReportHolder()

def get_conf(name):
    config = {
        'feed_type': 'tweet',
        'channel_type': 'twitter',
        'publisher_type': 'twitter',
        'publisher_feed': 'twitter stream'
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
        return holder.provide_report(report_id)
    except:
        return None

twt_take = Blueprint('twt_take', __name__)

@twt_take.route('/newstwister/tweets/<tweet_id>', defaults={}, methods=['POST'], strict_slashes=False)
def take_twt(tweet_id):
    from citizendesk.twt_ingest.process import do_post

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
    except:
        json_data = None

    if not json_data:
        logger.info('data not provided in the request')
        return ('Data not provided', 404,)
    for part in ['filter', 'tweet', 'endpoint']:
        if (part not in json_data) or (not json_data[part]):
            logger.info('No ' + str(part) + ' provided')
            return ('No ' + str(part) + ' provided', 404,)

    tweet = json_data['tweet']
    feed_filter = json_data['filter']
    endpoint = json_data['endpoint']

    try:
        res = do_post(holder, tweet_id, tweet, feed_filter, endpoint, client_ip)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return ('tweet received\n\n', 200,)
    except Exception as exc:
        logger.warning('problem on tweet processing or saving')
        return ('problem on tweet processing or saving', 404,)

