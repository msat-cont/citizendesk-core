#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
try:
    from citizendesk.feeds.sms.external import frontlinesms as controller
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

from citizendesk.feeds.sms.common.utils import get_conf, gen_id
from citizendesk.feeds.sms.common.utils import extract_tags as _extract_tags
from citizendesk.common.utils import get_boolean as _get_boolean

'''
For preparation of message sending
'''

def prepare_sms_send_report(targets, recipients, message, user_id=None, language=None, sensitive=None, client_ip=None):
    ''' preparing an sms-based report when the sms is sent not as a reply, i.e. starting a new session for it '''

    channel_type = get_conf('channel_type')
    channel_value = get_conf('channel_value_send')
    feed_type = get_conf('feed_type')

    channel = {
        'type': channel_type,
        'value': channel_value,
        'filter': None,
        'reasons': None,
        'request': None
    }

    current_timestamp = datetime.datetime.utcnow()

    doc = {
        'report_id': gen_id(feed_type, channel_type, channel_value, current_timestamp), # to generate the report_id
        'channels': [channel],
        'recipients': recipients,
        'authors': [], # no citizen here
        'endorsers': [], # no citizen here
        'publisher': get_conf('publisher'),
        'feed_type': feed_type,
        'parent_id': None, # not a reply here
        'session': None,
        'user_id': user_id, # who requested the sending, if not automatic
        'pinned_id': None,
        'coverage_id': None,
        'language': language,
        'produced': current_timestamp,
        'created': current_timestamp,
        'assignments': [],
        'original_id': None,
        'original': {'message': message},
        'texts': [{'original': message, 'transcript': None}],
        'tags': [], # we shall extract possible #tags, alike at sms receiving
        'is_published': False,
        'sensitive': None,
        'summary': False,
        'local': True,
        'targets': targets, # alias_ids and/or group_ids for replies, on sent reports
        'proto': False,
        'client_ip': client_ip # for logging
    }

    if sensitive is not None:
        doc['sensitive'] = _get_boolean(sensitive)

    doc['session'] = doc['report_id']

    doc['tags'] = _extract_tags(message)

    return doc

def prepare_sms_reply_report(report, targets, recipients, message, user_id=None, language=None, sensitive=None, client_ip=None):
    ''' preparing an sms-based report when the sms is sent as a reply, i.e. continuing a previous session '''

    if (type(report) is not dict):
        return None
    if ('session' not in report) or (not report['session']):
        return None
    if ('report_id' not in report) or (not report['report_id']):
        return None

    channel_type = get_conf('channel_type')
    channel_value = get_conf('channel_value_send')
    feed_type = get_conf('feed_type')

    channel = {
        'type': channel_type,
        'value': channel_value,
        'filter': None,
        'reasons': None,
        'request': None
    }

    current_timestamp = datetime.datetime.utcnow()

    doc = {
        'report_id': gen_id(feed_type, channel_type, channel_value, current_timestamp), # to generate the report_id
        'channels': [channel],
        'recipients': recipients,
        'authors': [], # no citizen here
        'endorsers': [], # no citizen here
        'publisher': get_conf('publisher'),
        'feed_type': feed_type,
        'parent_id': report['report_id'], # since a reply here
        'session': report['session'], # since a reply here
        'user_id': user_id, # who requested the sending, if not automatic
        'pinned_id': None,
        'coverage_id': None,
        'language': language,
        'produced': current_timestamp,
        'created': current_timestamp,
        'assignments': [],
        'original_id': None,
        'original': {'message': message},
        'texts': [{'original': message, 'transcript': None}],
        'tags': [], # we shall extract possible #tags, alike at sms receiving
        'is_published': False,
        'sensitive': None,
        'summary': False,
        'local': True,
        'targets': targets, # alias_ids and/or group_ids for replies, on sent reports
        'proto': False,
        'client_ip': client_ip # for logging
    }

    if sensitive is not None:
        doc['sensitive'] = _get_boolean(sensitive)

    doc['tags'] = _extract_tags(message)

    if ('pinned_id' in report) and report['pinned_id']:
        doc['pinned_id'] = report['pinned_id']

    if ('coverage_id' in report) and report['coverage_id']:
        doc['coverage_id'] = report['coverage_id']

    if ('assignments' in report) and report['assignments']:
        doc['assignments'] = report['assignments']

    return doc

