#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json
from citizendesk.outgest.liveblog.utils import get_conf, cid_from_update
from citizendesk.outgest.liveblog.storage import FIELD_UPDATED_USER

TEXTS_SEPARATOR = '<br>'
NOTICES_USED = ['before', 'after']

SMS_CONTENT_START = '<h3><a href="" target="_blank"></a></h3><div class="result-description"></div><!-- p.result-description tag displays for:> internal link> twitter> google link> google news> google images> flickr> youtube> soundcloud-->'

DEFAULT_AUTHOR_NAME = get_conf('default_report_author_name')
if not DEFAULT_AUTHOR_NAME:
    DEFAULT_AUTHOR_NAME = 'Citizen Desk'

DEFAULT_AUTHOR = {
    'Source': {
        'Name': 'citizen_desk',
    },
    'User': {
        'FirstName': DEFAULT_AUTHOR_NAME,
        'MetaDataIcon': {'href': get_conf('default_report_author_icon')},
    },
}
if get_conf('default_report_author_uuid'):
    DEFAULT_AUTHOR['User']['Uuid'] = get_conf('default_report_author_uuid')

DEFAULT_CREATOR = {
    'MetaDataIcon': {'href': get_conf('default_report_author_icon')},
    'FirstName': DEFAULT_AUTHOR_NAME,
}
if get_conf('default_report_author_uuid'):
    DEFAULT_CREATOR['Uuid'] = get_conf('default_report_author_uuid')

def extract_texts(report):
    # taking the (transcribed) texts

    texts = []
    if ('texts' in report) and (type(report['texts']) in (list, tuple)):
        for one_text in report['texts']:
            if type(one_text) is not dict:
                continue
            if ('transcript' in one_text) and one_text['transcript']:
                texts.append(one_text['transcript'])
                continue
            if ('original' in one_text) and one_text['original']:
                texts.append(one_text['original'])
                continue

    return texts

def extract_annotation(report):
    # taking editorial comments

    notices = {}
    annotation = {}
    for notice_type in NOTICES_USED:
        notices[notice_type] = []
        annotation[notice_type] = None

    if ('notices_outer' in report) and (type(report['notices_outer']) in (list, tuple)):
        for one_notice in report['notices_outer']:
            if type(one_notice) is not dict:
                continue
            if ('what' not in one_notice) or not one_notice['what']:
                continue
            if ('where' not in one_notice) or (one_notice['where'] not in NOTICES_USED):
                continue
            notices[one_notice['where']].append(one_notice['what'])

    for notice_type in NOTICES_USED:
        if notices[notice_type]:
            annotation[notice_type] = TEXTS_SEPARATOR.join(notices[notice_type])

    return annotation

'''
regarding SMS, liveblog creates them via GET requests, like
http://sourcefabric.superdesk.pro/resources/SMS/Inlet/other/Post/Push?phoneNumber=1234&messageText=hello+world
it creates a post, then if a blog subscribes to SMS feed, a (new) blogpost is created (for each such subscribed blog)
'''
def adapt_sms_report(report):
    parts = {'content':'', 'meta':''}

    texts = extract_texts(report)

    # https://github.com/superdesk/Live-Blog/blob/master/plugins/livedesk/gui-resources/templates/items/base.dust#L81
    parts['content'] = SMS_CONTENT_START + TEXTS_SEPARATOR.join(texts)

    annotation = extract_annotation(report)
    parts['meta'] = json.dumps({'annotation': annotation})

    return parts

def adapt_tweet_report(report):
    parts = {'content':'', 'meta':''}

    if ('original' in report) and (type(report['original']) is dict):
        if ('text' in report['original']) and report['original']['text']:
            parts['content'] = report['original']['text']

    parts_meta = {}

    # for a tweet, the meta is the original tweet with the additions below
    if ('original' in report) and (type(report['original']) is dict):
        parts_meta = report['original']

        # these metadata probably set by twitter in liveblog; trying to avoid it
        # parts_meta['metadata'] = {'result_type':'', 'iso_language_code':''}

        # https://github.com/superdesk/Live-Blog/blob/master/plugins/livedesk/gui-resources/scripts/js/providers/twitter.js#L204
        parts_meta['api_version'] = '1.1';
        if ('user' in report['original']) and (type(report['original']['user']) is dict):
            if 'profile_image_url' in report['original']['user']:
                parts_meta['profile_image_url'] = report['original']['user']['profile_image_url']
            if 'name' in report['original']['user']:
                parts_meta['from_user_name'] = report['original']['user']['name']
            if 'screen_name' in report['original']['user']:
                parts_meta['from_user'] = report['original']['user']['screen_name']
        if 'created_at' in parts_meta:
            parts_meta['created_at_formated'] = parts_meta['created_at']

    #https://github.com/superdesk/Live-Blog/blob/master/plugins/livedesk/gui-resources/scripts/js/providers/twitter.js#L574
    parts_meta['type'] = 'natural'

    annotation = extract_annotation(report)
    parts_meta['annotation'] = annotation

    parts['meta'] = json.dumps(parts_meta)

    return parts

def adapt_plain_report(report):
    parts = {'content':'', 'meta':''}

    texts = extract_texts(report)
    parts['content'] = TEXTS_SEPARATOR.join(texts)

    annotation = extract_annotation(report)
    parts['meta'] = json.dumps({'annotation': annotation})

    return parts

def get_sms_report_author(report, user):

    use_uuid = get_conf('sms_report_creator_uuid')
    use_icon = get_conf('sms_report_creator_icon')

    author = {
        'Source': {
            'Name': 'sms_ingest', # actually not used, since providing user below; otherwise coverage name could be used
        },
        'User': {
            'FirstName': 'SMS',
            'MetaDataIcon': {'href': use_icon},
        },
    }

    if use_uuid:
        author['User']['Uuid'] = use_uuid

    return author

def get_sms_report_creator(report, user):

    use_uuid = get_conf('sms_report_creator_uuid')
    use_icon = get_conf('sms_report_creator_icon')

    creator = {
        'FirstName': 'SMS',
        'MetaDataIcon': {'href': use_icon},
    }

    if use_uuid:
        creator['Uuid'] = use_uuid

    return creator

def get_tweet_report_author(report, user):

    author = {
        'Source': {
            'Name': 'twitter',
        },
    }

    return author

def get_tweet_report_creator(report, user):

    if not user:
        return DEFAULT_CREATOR

    icon_url = None
    if ('picture_url' in user) and user['picture_url']:
        icon_url = user['picture_url']

    creator = {
        'MetaDataIcon': {'href': icon_url},
    }

    if ('uuid' in user) and user['uuid']:
        creator['Uuid'] = user['uuid']

    if (FIELD_UPDATED_USER in user) and user[FIELD_UPDATED_USER]:
        creator['Cid'] = cid_from_update(user[FIELD_UPDATED_USER])

    first_name = None
    if ('first_name' in user) and user['first_name']:
        creator['FirstName'] = user['first_name']

    last_name = None
    if ('last_name' in user) and user['last_name']:
        creator['LastName'] = user['last_name']

    return creator

def get_plain_report_author(report, user):

    if not user:
        return DEFAULT_AUTHOR

    icon_url = None
    if ('picture_url' in user) and user['picture_url']:
        icon_url = user['picture_url']

    author = {
        'Source': {
            'Name': 'internal',
        },
        'User': {
            'MetaDataIcon': {'href': icon_url},
        },
    }

    if ('uuid' in user) and user['uuid']:
        author['User']['Uuid'] = user['uuid']

    if (FIELD_UPDATED_USER in user) and user[FIELD_UPDATED_USER]:
        author['User']['Cid'] = cid_from_update(user[FIELD_UPDATED_USER])

    if ('first_name' in user) and user['first_name']:
        author['User']['FirstName'] = user['first_name']

    if ('last_name' in user) and user['last_name']:
        author['User']['LastName'] = user['last_name']

    return author

def get_plain_report_creator(report, user):

    if not user:
        return DEFAULT_CREATOR

    icon_url = None
    if ('picture_url' in user) and user['picture_url']:
        icon_url = user['picture_url']

    creator = {
        'MetaDataIcon': {'href': icon_url},
    }

    if ('uuid' in user) and user['uuid']:
        creator['Uuid'] = user['uuid']

    if (FIELD_UPDATED_USER in user) and user[FIELD_UPDATED_USER]:
        creator['Cid'] = cid_from_update(user[FIELD_UPDATED_USER])

    first_name = None
    if ('first_name' in user) and user['first_name']:
        creator['FirstName'] = user['first_name']

    last_name = None
    if ('last_name' in user) and user['last_name']:
        creator['LastName'] = user['last_name']

    return creator

