#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json
from citizendesk.ingest.sms.connect import get_conf, gen_id, get_sms
from citizendesk.ingest.sms.sms_replier import send_sms

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

def ask_sender(phone_number):
    message = 'Dear citizen, could you tell us you geolocation, please?'
    unicode_flag = False
    #send_script = get_conf('send_script_path')
    send_config = get_conf('send_config_path')
    #try:
    #    subprocess.call([send_script, send_config, phone_number, message, unicode_flag])
    #except:
    #    logging.error('can not send SMS to: ' + str(phone_number))
    #    return False
    send_sms(send_config, phone_number, message, unicode_flag)

    return True

def do_post(holder, params, client_ip):

    feed_name = params['feed']
    phone_number = params['phone']

    feed_type = get_conf('feed_type')
    received = params['time']
    if not received:
        received = datetime.datetime.now()

    feed_filter = None

    channels = [{'type': get_conf('channel_type'), 'value': feed_name, 'filter': feed_filter}],
    publishers = []
    authors = {'authority': 'telco', 'identifiers': [{'type': 'phone_number', 'value': phone_number}]}
    endorsers = []

    original = params['text']
    texts = [params['text']]
    tags = []
    if params['text']:
        for word in params['text'].split(' '):
            if word.startswith('#'):
                use_tag = word[1:]
                if use_tag:
                    tags.append(use_tag)

    # session_id should only be set here when reusing an old one
    session = None
    new_session = True
    parent_id = None

    session_look_spec = {'channel': {'type': channels[0]['type']}, 'author': authors[0]}
    force_new_session = holder.get_force_new_session(session_look_spec)
    if force_new_session:
        holder.clear_force_new_session(session_look_spec, True)
    else:
        last_report = holder.find_last_session({'channels': channels[0], 'authors': authors[0]})
        if last_report:
            if is_within_session(last_report['received'], received):
                parent_id = last_report['report_id']
                session = last_report['session']
                new_session = False

    report = {}
    report['report_id'] = gen_id(feed_type, phone_number)
    report['parent_id'] = parent_id
    report['client_ip'] = client_ip
    report['feed_type'] = feed_type
    report['feed_spec'] = None
    report['produced'] = received
    report['session'] = session
    report['channels'] = channels
    report['authors'] = authors
    report['original'] = original
    report['texts'] = texts
    report['tags'] = tags

    report['proto'] = False

    holder.save_report(report)

    if new_session:
        ask_sender()

    return (200, 'SMS received\n\n')

