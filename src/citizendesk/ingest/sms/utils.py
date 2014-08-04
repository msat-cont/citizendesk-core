#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, random
try:
    import yaml
except:
    #logging.error('Can not load YAML support')
    sys.exit(1)
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger
from citizendesk.common.holder import ReportHolder
from citizendesk.feeds.sms.common.utils import get_conf, normalize_phone_number

holder = ReportHolder()

COLL_CONFIG = 'core_config'

DEFAULT_TIME_DELAY = 1 # 1h

def load_send_sms_config(config_path):
    global config

    if not config_path:
        return

    config_data = {}
    try:
        fh = open(config_path)
        rd = fh.read()
        fh.close()
        yl = yaml.load_all(rd)
        config_data = yl.next()
        yl.close()
    except:
        #logging.error('Can not read config for SMS sending: ' + str(conf_path))
        return False

    if not config_data:
        return False

    sms_prefix = 'sms_'
    for key in config:
        take_key = key
        if take_key.startswith(sms_prefix):
            take_key = take_key[len(sms_prefix):]
        if take_key in config_data:
            config[key] = config_data[take_key]

    try:
        if config['sms_session_duration'] is not None:
            config['sms_session_duration'] = int(config['sms_session_duration'])
    except:
        config['sms_session_duration'] = None

    return True

config = {
    'sms_gateway_url': None,
    'sms_gateway_key': None,
    'sms_session_duration': DEFAULT_TIME_DELAY,
    'sms_reply_send': None,
    'sms_reply_message': None,
    'sms_confirm_send': None,
    'sms_confirm_message': None,
    'sms_password_key': None,
    'sms_phone_param': 'phone',
    'sms_text_param': 'text',
    'sms_feed_param': 'feed',
    'sms_time_param': 'time',
    'sms_pass_param': 'pass',
}

def get_sms(phone_number):
    session_info = None

    phone_number_normalized = normalize_phone_number(phone_number)
    if not phone_number_normalized:
        return None

    feed_type = get_conf('feed_type')
    authority = get_conf('authority')
    channel_value_send = get_conf('channel_value_send')
    channel_value_receive = get_conf('channel_value_receive')

    sess_spec_sent = {
        'feed_type': feed_type,
        'channels': {'$elemMatch': {'value': channel_value_send}},
        'recipients': {'$elemMatch': {'authority': authority, 'identifiers.user_id_search': phone_number_normalized}}
    }
    res = holder.find_last_session(sess_spec_sent)
    if (type(res) is not dict) or ('produced' not in res):
        res = None
    if res:
        session_info = res

    sess_spec_received = {
        'feed_type': feed_type,
        'channels': {'$elemMatch': {'value': channel_value_receive}},
        'authors': {'$elemMatch': {'authority': authority, 'identifiers.user_id_search': phone_number_normalized}}
    }
    res = holder.find_last_session(sess_spec_received)
    if (type(res) is not dict) or ('produced' not in res):
        res = None
    if res:
        if not session_info:
            session_info = res
        else:
            if res['produced'] >= session_info['produced']:
                session_info = res

    return session_info

def get_sms_configuration(db):
    global config

    sms_config = {}
    for key in config:
        sms_config[key] = config[key]

    found_config = db[COLL_CONFIG].find_one({'_type': 'sms'})
    if found_config and (type(found_config) is dict):
        for key in sms_config:
            if (key in found_config) and (found_config[key] is not None):
                sms_config[key] = found_config[key]

    try:
        # delays within sessions specified in hours, put into secs
        if (sms_config['sms_session_duration'] is not None) and (0 < sms_config['sms_session_duration']):
            sms_config['sms_session_duration'] = sms_config['sms_session_duration'] * 3600
    except:
        sms_config['sms_session_duration'] = None

    return sms_config

