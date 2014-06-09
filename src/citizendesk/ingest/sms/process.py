#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json

from citizendesk.ingest.sms.utils import holder
from citizendesk.ingest.sms.utils import get_conf, gen_id, get_sms
#from citizendesk.ingest.sms.sms_replier import send_sms

COLL_REPLY_MESSAGES = 'reply_messages'

def is_within_session(last_received, current_received):
    max_diff = get_conf('time_delay')
    if 0 > max_diff:
        return True
    if 0 == max_diff:
        return False

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
    if time_diff.seconds <= max_diff:
        return True

    return False

def ask_sender(db, session_start, orig_report, alias_id, phone_number):
    # by now: general config in a config file
    # by phone_number: in citizen_alias structure

    # message = None
    # if session_start:
    #   to_send = sms_reply_send()
    #   to_send_spec = sms_reply_send(phone_number)
    #   if to_send_spec is not None:
    #       to_send = to_send_spec
    #   if to_send:
    #       message = sms_reply_message()
    #       message_spec = sms_reply_message(phone_number)
    #       if message_spec:
    #           message = message_spec
    # else:
    #   to_send = sms_confirm_send()
    #   to_send_spec = sms_confirm_send(phone_number)
    #   if to_send_spec is not None:
    #       to_send = to_send_spec
    #   if to_send:
    #       message = sms_confirm_message()
    #       message_spec = sms_confirm_message(phone_number)
    #       if message_spec:
    #           message = message_spec

    message = None
    if session_start:
        get_conf('send_reply')

    else:
        pass


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
            return False

    use_targets = [{'type':'citizen_alias', 'value':alias_id}]
    use_recipients = [{'authority':'telco', 'identifiers':[{'type':'phone_number', 'value':phone_number}]}]
    use_phone_numbers = [phone_number]

    doc = _prepare_sms_reply_report(orig_report, use_targets, use_recipients, message)

    #send_sms(send_config, phone_number, message)
    doc_id = report_holder.save_report(report)
    if not doc_id:
        return (False, 'report could not be saved')

    connector = controller.SMSConnector(sms_gateway_url, sms_gateway_key)
    res = connector.send_sms(message, {'phone_numbers': use_phone_numbers})
    if not res[0]:
        report_holder.delete_report(doc_id)
        return (False, 'message could not be sent', res[1])

    return True

def assure_citizen_alias(phone_number):
    ''' create citizen alias if does not exist yet '''

    from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_phone_number as get_one_citizen_alias_by_phone_number
    alias_res = get_one_citizen_alias_by_phone_number(phone_number)
    if alias_res[0]:
        if (type(alias_res[1]) is not dict) or ('_id' not in alias_res[1]):
            return (False, 'wrong loaded citizen alias structure')
        return (True, {'_id': alias['_id']})

    authority = get_conf('authority')
    phone_identifier_type = get_conf('phone_identifier_type')

    alias_new = {
        'authority': authority,
        'identifiers': [{'type':phone_identifier_type, 'value':phone_number}],
        'verified': False,
        'local': False
    }

    alias_id = citizen_holder.save_alias(alias_new)
    if not alias_id:
        return (False, 'can not save citizen alias info')

    return (True, {'_id': alias_id})

def do_post(db, params, client_ip):
    '''
    * assure citizen_alias exists (i.e. create/save if does not yet)
    * find if following a previous report (incl. taking its session)
    * create and save the report
    * if starting a new session and with auto-replies:
        * create a reply-report
        * send a reply message (via gateway)
    '''

    # taking given params
    feed_type = get_conf('feed_type')
    publisher = get_conf('publisher')

    feed_name = params['feed']
    phone_number = params['phone']
    received = params['time']
    message = params['text']

    timestamp = datetime.datetime.now()

    # assuring the citizen
    alias_id = None
    alias_res = assure_citizen_alias(phone_number)
    if alias_res[0]:
        alias_id = alias_res[1]

    # finding the followed report
    last_report = get_sms(phone_number)
    if last_report:
        for key in ['produced', 'session', 'report_id']:
            if key not in last_report:
                last_report = None

    # creating the report
    sms_filter = None
    if feed_name:
        sms_filter = {'feed_name': feed_name}

    channels = [{'type': 'sms', 'value': 'received', 'filter': sms_filter, 'request': None, 'reasons': None}]
    authors = [{'authority': 'telco', 'identifiers': [{'type': 'phone_number', 'value': phone_number}]}]
    endorsers = []

    original = {'message': message}
    texts = [{'original': message, 'transcript': None}]
    tags = []
    if message:
        tags = _extract_tags(message)

    report_id = gen_id(channel_type, channel_value, None, timestamp)
    session = report_id
    parent_id = None
    new_session = True

    pinned_id = None
    assignments = []

    if last_report:
        if is_within_session(last_report['produced'], received):
            session = last_report['session']
            parent_id = last_report['report_id']
            if 'pinned_id' in last_report:
                pinned_id = last_report['pinned_id']
            if 'assignments' in last_report:
                assignments = last_report['assignments']
            new_session = False

    report = {}
    report['report_id'] = report_id
    report['parent_id'] = parent_id
    report['client_ip'] = client_ip
    report['feed_type'] = feed_type
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

    report_id = holder.save_report(report)

    # checking whether to send auto-reply; sending it if it shall be sent
    #if get_conf('send_reply') and new_session:
    #    ask_sender(db, report, alias_id, phone_number)
    ask_sender(db, new_session, report, alias_id, phone_number)

    return (200, 'SMS received\n\n')

