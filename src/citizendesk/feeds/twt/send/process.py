#!/usr/bin/env python
#
# Citizen Desk
#

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
from citizendesk.feeds.twt.send.storage import collection, schema
from citizendesk.feeds.twt.report.storage import collection as collection_reports
from citizendesk.feeds.twt.authorized.storage import collection as collection_authorized
from citizendesk.feeds.twt.report.storage import FEED_TYPE

'''
Requests to send a tweet, incl. a reply to a tweet
'''

def do_post_send(db, sender_url, authorized_id, user_id, endpoint_id, tweet_spec, report_id=None):
    '''
    sends (a reply to) a tweet
    after it is sent and received, local=True, and user_id=user_id are set in the report
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if not authorized_id:
        return (False, 'authorized_id not specified')
    if not user_id:
        return (False, 'user_id not specified')
    if not endpoint_id:
        return (False, 'endpoint_id not specified')

    if type(tweet_spec) is not dict:
        return (False, 'unknown form of tweet spec')
    if ('message' not in tweet_spec) or (not tweet_spec['message']):
        return (False, 'message text not provided')

    follow_part = []
    tweet_data = {
        'endpoint_id': endpoint_id,
        'status': tweet_spec['message'],
        'filter': {},
    }

    if ('sensitive' in tweet_spec) and (tweet_spec['sensitive'] is not None):
        sensitive = _get_boolean(tweet_spec['sensitive'])
        if sensitive:
            tweet_data['possibly_sensitive'] = 'true'

    if ('display_coordinates' in tweet_spec) and (tweet_spec['display_coordinates'] is not None):
        display_coordinates  = _get_boolean(tweet_spec['display_coordinates'])
        if display_coordinates:
            tweet_data['display_coordinates'] = 'true'
        else:
            tweet_data['display_coordinates'] = 'false'

    for key in ['lat', 'long', 'place_id']:
        if (key in tweet_spec) and (tweet_spec[key]):
            try:
                tweet_data[key] = str(tweet_spec[key])
            except:
                return (False, 'wrong "' + str(key) + '" part in tweet spec')

    if report_id is not None:
        report_id = _get_id_value(report_id)

        search_spec = {'feed_type': FEED_TYPE}
        if type(report_id) is ObjectId:
            search_spec['_id'] = report_id
        else:
            search_spec['report_id'] = report_id

        coll = db[collection_reports]
        report = coll.find_one(search_spec)
        if not report:
            return (False, 'specified report not found')

        try:
            orig_user_screen_name = str(report['original']['user']['screen_name']).lower()
            if orig_user_screen_name not in follow_part:
                follow_part.append(orig_user_screen_name)
        except:
            return (False, 'can not find the original tweet sender')

        check_inclusion = '@' + orig_user_screen_name.lower()
        try:
            if check_inclusion not in tweet_spec['message'].lower():
                return (False, 'mentioning the original tweet sender not found in the tweet text')
        except:
            return (False, 'can not check inclusion of the original tweet sender')

        try:
            tweet_data['in_reply_to_status_id'] = str(report['original_id'])
        except:
            return (False, 'can not find id_str of the original tweet')

    coll = db[collection_authorized]
    authorized_id = _get_id_value(authorized_id)

    authorized_data = coll.find_one({'_id': authorized_id})
    if not authorized_data:
        return (False, 'saved report on the send-tweet not found')

    try:
        authorized_spec = {
            'consumer_key': authorized_data['spec']['app_consumer_key'],
            'consumer_secret': authorized_data['spec']['app_consumer_secret'],
            'access_token_key': authorized_data['spec']['authorized_access_token_key'],
            'access_token_secret': authorized_data['spec']['authorized_access_token_secret'],
        }
        sender_screen_name = str(authorized_data['spec']['screen_name_search'])
        if sender_screen_name not in follow_part:
            follow_part.append(sender_screen_name)
    except Exception as exc:
        return (False, 'authorized info does not contain all the required data: ' + str(exc))

    for key in authorized_spec:
        if not authorized_spec[key]:
            return (False, 'the "' + str(key) + '" part of authorized info is empty')

    tweet_data['filter']['follow'] = follow_part

    connector = controller.NewstwisterConnector(sender_url)
    res = connector.send_tweet(authorized_spec, tweet_data)
    if not res[0]:
        err_msg = 'error during send-tweet request dispatching: ' + res[1]
        return (False, err_msg)

    ret_envelope = res[1]
    if type(ret_envelope) is not dict:
        return (False, 'unknown form of returned send-tweet data: ' + str(type(ret_envelope)))

    if ('status' not in ret_envelope) or (not ret_envelope['status']):
        err_msg = ''
        if ('error' in ret_envelope) and (ret_envelope['error']):
            err_msg = ': ' + str(ret_envelope['error'])
        return (False, 'status not acknowledged in returned send-tweet data' + err_msg)
    if ('data' not in ret_envelope) or (not ret_envelope['data']):
        return (False, 'payload not provided in returned send-tweet data')

    ret_data = ret_envelope['data']
    if type(ret_data) is not dict:
        return (False, 'unknown form of returned payload in send-tweet data: ' + str(type(ret_data)))

    if 'id_str' not in ret_data:
        return (False, 'returned send-tweet data without tweet identifier')

    coll = db[collection_reports]
    saved_tweet = coll.find_one({'original_id': ret_data['id_str']})
    if not saved_tweet:
        return (False, 'saved report on the send-tweet not found')

    doc_id = saved_tweet['_id']

    user_id = _get_id_value(user_id)
    coll.update({'_id': doc_id}, {'$set': {'local': True, 'user_id': user_id, 'proto': False}})

    return (True, {'_id': doc_id})

