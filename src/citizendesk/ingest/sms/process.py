#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json

from citizendesk.ingest.sms.connect import get_conf, gen_id, get_sms
from citizendesk.ingest.sms.sms_replier import send_sms

COLL_REPLY_MESSAGES = 'reply_messages'

def is_within_session(last_received, current_received):
    if not last_received:
        return False
    if not current_received:
        return False

    try:
        if type(last_received) is not datetime.datetime:
            dt_format = '%Y-%m-%dT%H:%M:%S'
            if '.' in last_received:
                dt_format = '%Y-%m-%dT%H:%M:%S.%f'
            last_received = datetime.datetime.strptime(last_received, dt_format)
    except:
        return False

    try:
        if type(current_received) is not datetime.datetime:
            dt_format = '%Y-%m-%dT%H:%M:%S'
            if '.' in current_received:
                dt_format = '%Y-%m-%dT%H:%M:%S.%f'
            current_received = datetime.datetime.strptime(current_received, dt_format)
    except:
        return False

    time_diff = current_received - last_received
    if time_diff.seconds <= get_conf('time_delay'):
        return True

    return False

def ask_sender(db, phone_number):

    message = get_conf('reply_message')

    specific_message = db[COLL_REPLY_MESSAGES].find_one({'phone_number': phone_number})
    if specific_message and ('reply_message' in specific_message):
        message = specific_message['reply_message']

    if not message:
        return False

    send_config = get_conf('send_config')
    if not send_config:
        return False

    for param in ['method', 'url', 'phone_param', 'text_param']:
        if (param not in send_config) or (not send_config[param]):
            False

    send_sms(send_config, phone_number, message)

    return True

def do_post(db, holder, params, client_ip):
    feed_type = get_conf('feed_type')
    publisher = get_conf('publisher')
    feed_filter = None

    feed_name = params['feed']
    phone_number = params['phone']
    received = params['time']

    channels = [{'type': feed_name, 'value': phone_number, 'filter': None, 'request': None}]
    authors = [{'authority': 'telco', 'identifiers': [{'type': 'phone_number', 'value': phone_number}]}]
    endorsers = []

    original = params['text']
    texts = [{'original': params['text'], 'transcript': None}]
    tags = []
    if params['text']:
        for word in params['text'].split(' '):
            if word.startswith('#'):
                use_tag = word[1:]
                if use_tag:
                    tags.append(use_tag)

    report_id = gen_id(feed_type, phone_number)
    session = report_id
    parent_id = None
    new_session = True

    pinned_id = None
    assignments = []

    last_report = get_sms(feed_name, phone_number)
    if last_report:
        if is_within_session(last_report['produced'], received):
            session = last_report['session']
            parent_id = last_report['report_id']
            pinned_id = last_report['pinned_id']
            assignments = last_report['assignments']
            new_session = False

    report = {}
    report['report_id'] = report_id
    report['parent_id'] = parent_id
    report['client_ip'] = client_ip
    report['feed_type'] = feed_type
    report['feed_spec'] = None
    report['produced'] = received
    report['session'] = session
    report['publisher'] = publisher
    report['channels'] = channels
    report['authors'] = authors
    report['original'] = original
    report['texts'] = texts
    report['tags'] = tags

    report['pinned_id'] = pinned_id
    report['assignments'] = assignments

    report['proto'] = False

    holder.save_report(report)

    if get_conf('send_reply') and new_session:
        ask_sender(db, phone_number)

    return (200, 'SMS received\n\n')

