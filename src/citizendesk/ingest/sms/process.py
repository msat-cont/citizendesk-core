#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json
try:
    from citizendesk.feeds.sms.external import frontlinesms as controller
except:
    controller = None

from citizendesk.ingest.sms.utils import holder as report_holder
from citizendesk.ingest.sms.utils import get_sms
from citizendesk.feeds.sms.common.reports import prepare_sms_reply_report as _prepare_sms_reply_report
from citizendesk.feeds.sms.common.utils import get_conf, gen_id, citizen_holder, PHONE_NUMBER_ID_KEYS
from citizendesk.feeds.sms.common.utils import extract_tags as _extract_tags
from citizendesk.common.utils import get_logger

def is_within_session(last_received, current_received, config):
    max_diff = config['sms_session_duration']

    if (0 > max_diff) or (max_diff is None):
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
    if time_diff.total_seconds() <= max_diff:
        return True

    return False

def ask_sender(db, session_start, orig_report, alias_info, phone_number, common_config):
    # for now, general config in a config file, or 'cd_config' collection in 'sms' document
    # by phone_number: in citizen_alias structure

    use_config = {
        'sms_reply_send': None,
        'sms_reply_message': None,
        'sms_confirm_send': None,
        'sms_confirm_message': None,
    }

    for key in use_config:
        if key in common_config:
            use_config[key] = common_config[key]

    alias_config = {}
    if ('config' in alias_info) and (type(alias_info['config']) is dict):
        alias_config = alias_info['config']
    for key in use_config:
        if (key in alias_config) and (alias_config[key] is not None):
            use_config[key] = alias_config[key]

    message = None
    if session_start:
        to_send = use_config['sms_reply_send']
        if to_send:
            message = use_config['sms_reply_message']
    else:
        to_send = use_config['sms_confirm_send']
        if to_send:
            message = use_config['sms_confirm_message']

    if not message:
        return (True, None)

    if not controller:
        return (False, 'no sms gateway controller available')

    conf_alias_doctype = get_conf('alias_doctype')
    conf_authority = get_conf('authority')

    use_targets = [{'type':conf_alias_doctype, 'value':alias_info['_id']}]
    use_identifiers = {}
    for use_identity_key in PHONE_NUMBER_ID_KEYS:
        use_identifiers[use_identity_key] = phone_number
    use_recipients = [{'authority':conf_authority, 'identifiers':use_identifiers}]
    use_phone_numbers = [phone_number]

    doc = _prepare_sms_reply_report(orig_report, use_targets, use_recipients, message)
    if not doc:
        return (False, 'automatic report could not be prepared')
    doc['automatic'] = True

    doc_id = report_holder.save_report(doc)
    if not doc_id:
        return (False, 'automatic report could not be saved')

    sms_gateway_url = common_config['sms_gateway_url']
    sms_gateway_key = common_config['sms_gateway_key']

    connector = controller.SMSConnector(sms_gateway_url, sms_gateway_key)
    res = connector.send_sms(message, {'phone_numbers': use_phone_numbers})
    if not res[0]:
        report_holder.delete_report(doc_id)
        return (False, 'automatic message could not be sent', res[1])

    return (True, {'_id': doc_id})

def assure_citizen_alias(db, phone_number):
    ''' create citizen alias if does not exist yet '''

    from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_phone_number as get_one_citizen_alias_by_phone_number
    from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_id as get_one_citizen_alias_by_id
    alias_res = get_one_citizen_alias_by_phone_number(db, phone_number)
    if alias_res[0]:
        if (type(alias_res[1]) is not dict) or ('_id' not in alias_res[1]):
            return (False, 'wrong loaded citizen alias structure')
        return (True, alias_res[1])

    authority = get_conf('authority')

    use_identifiers = {}
    for use_identity_key in PHONE_NUMBER_ID_KEYS:
        use_identifiers[use_identity_key] = phone_number

    alias_new = {
        'authority': authority,
        'identifiers': use_identifiers,
        'verified': False,
        'local': False
    }

    alias_id = citizen_holder.save_alias(alias_new)
    if not alias_id:
        return (False, 'can not save citizen alias info')

    alias_res = get_one_citizen_alias_by_id(db, alias_id)
    if (not alias_res[0]) or (type(alias_res[1]) is not dict) or ('_id' not in alias_res[1]):
        return (False, 'wrong reloaded citizen alias structure')

    return alias_res

def do_post(db, params, main_config, client_ip):
    '''
    * assure citizen_alias exists (i.e. create/save if does not yet)
    * find if following a previous report (incl. taking its session)
    * create and save the report
    * if starting a new session and with auto-replies:
        * create a reply-report
        * send a reply message (via gateway)
    '''
    logger = get_logger()

    # taking given params
    feed_type = get_conf('feed_type')
    publisher = get_conf('publisher')

    feed_name = params['feed']
    phone_number = params['phone']
    message = params['text']
    received = params['time']

    timestamp = datetime.datetime.now()

    # assuring the citizen
    alias_id = None
    alias_info = None
    alias_res = assure_citizen_alias(db, phone_number)
    if alias_res[0]:
        alias_info = alias_res[1]
        alias_id = alias_info['_id']

    # finding the followed report
    last_report = get_sms(phone_number)
    if last_report:
        for key in ['produced', 'session', 'report_id']:
            if key not in last_report:
                last_report = None

    # creating the report
    authority = get_conf('authority')
    channel_type = get_conf('channel_type')
    channel_value_receive = get_conf('channel_value_receive')

    sms_filter = None
    if feed_name:
        sms_filter = {'feed_name': feed_name}

    use_identifiers = {}
    for use_identity_key in PHONE_NUMBER_ID_KEYS:
        use_identifiers[use_identity_key] = phone_number

    channels = [{'type': channel_type, 'value': channel_value_receive, 'filter': sms_filter, 'request': None, 'reasons': None}]
    authors = [{'authority': authority, 'identifiers': use_identifiers}]
    endorsers = []

    original = {'message': message}
    texts = [{'original': message, 'transcript': None}]
    tags = []
    if message:
        tags = _extract_tags(message)

    report_id = gen_id(feed_type, channel_type, channel_value_receive, timestamp)
    session = report_id
    parent_id = None
    new_session = True

    pinned_id = None
    assignments = []

    if last_report:
        if is_within_session(last_report['produced'], received, main_config):
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

    report_doc_id = report_holder.save_report(report)
    if not report_doc_id:
        return (False, 'can not save SMS report')

    report = report_holder.provide_report(feed_type, report_id)

    reply_res = ask_sender(db, new_session, report, alias_info, phone_number, main_config)
    if not reply_res[0]:
        reason = str(reply_res[1])
        if 2 < len(reply_res):
            reason += ', ' + str(reply_res[2])
        logger.warning('Issue during auto-reply SMS: ' + reason)

    return (True, str(report_doc_id))

