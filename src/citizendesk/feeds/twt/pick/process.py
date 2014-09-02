#!/usr/bin/env python
#
# Citizen Desk
#

import json, urllib2

import datetime
try:
    from citizendesk.feeds.twt.external import newstwister as controller
except:
    controller = None

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

from bson.objectid import ObjectId

from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_etag as _get_etag
from citizendesk.feeds.twt.pick.storage import collection, schema
from citizendesk.feeds.twt.report.storage import collection as collection_reports
from citizendesk.feeds.twt.report.storage import FEED_TYPE
from citizendesk.feeds.any.report.storage import FIELD_UPDATED

TWEET_DOMAIN = 'twitter.com'

'''
Requests to pick a tweet
'''

def do_post_pick(db, picker_url, user_id, endpoint_id, tweet_spec):
    '''
    picks a tweet
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if not user_id:
        return (False, 'user_id not specified')
    if not endpoint_id:
        return (False, 'endpoint_id not specified')

    if type(tweet_spec) is not dict:
        return (False, 'unknown form of tweet spec')

    tweet_id = None
    if ('tweet_id' in tweet_spec) and tweet_spec['tweet_id']:
        tweet_id = str(tweet_spec['tweet_id'])
    if (not tweet_id) and ('tweet_url' in tweet_spec) and tweet_spec['tweet_url']:
        tweet_url = str(tweet_spec['tweet_url']).lower()
        url_scheme, url_netloc, url_path, url_params, url_query, url_index = urllib2.urlparse.urlparse(tweet_url)
        if TWEET_DOMAIN != url_netloc:
            if url_path.startswith(TWEET_DOMAIN):
                url_netloc = TWEET_DOMAIN
                url_path = url_path[len(TWEET_DOMAIN):]
        if TWEET_DOMAIN != url_netloc:
            return (False, 'unknown tweet URL domain')
        path_parts = []
        for one_part in url_path.split('/'):
            if not one_part:
                continue
            path_parts.append(one_part)
        if 3 != len(path_parts):
            return (False, 'unrecognized tweet URL path')
        if path_parts[1] not in ('status', 'statuses'):
            return (False, 'unrecognized tweet URL path segments')
        tweet_id = path_parts[2].strip()
        if not tweet_id:
            return (False, 'tweet id part of provided URL is empty')

    if not tweet_id:
        return (False, 'no tweet specifier found')
    if not tweet_id.isdigit():
        return (False, 'tweet specifier is not a numerical string')

    pick_data = {
        'endpoint_id': endpoint_id,
        'tweet_id': tweet_id,
    }

    connector = controller.NewstwisterConnector(picker_url)
    res = connector.pick_tweet(pick_data)
    if not res[0]:
        err_msg = 'error during pick-tweet request dispatching: ' + res[1]
        return (False, err_msg)

    coll = db[collection_reports]
    saved_tweet = coll.find_one({'original_id': tweet_id})
    if not saved_tweet:
        return (False, 'saved report on the pick-tweet not found')

    doc_id = saved_tweet['_id']

    saved_update = {'proto': False}

    if ('user_id' not in saved_tweet) or (not saved_tweet['user_id']):
        user_id = _get_id_value(user_id)
        saved_update['user_id'] = user_id

    saved_update[FIELD_UPDATED] = datetime.datetime.utcnow()
    saved_update['_etag'] = _get_etag()

    coll.update({'_id': doc_id}, {'$set': saved_update})

    return (True, {'_id': doc_id})
