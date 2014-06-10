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

holder = ReportHolder()

COLL_CONFIG = 'cd_config'

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
    'phone_param': 'phone',
    'text_param': 'text',
    'feed_param': 'feed',
    'time_param': 'time',
}

def get_config(name):
    global config

    if name in config:
        return config[name]
    return None

def get_sms(feed_type, phone_number):
    session_info = None

    sess_spec_sent = {
        'feed_type': feed_type,
        'channels': {'$elemMatch': {'value': 'sent'}},
        'recipients': {'authority': 'telco', 'identifiers': {'type': 'phone_number', 'value': phone_number}}
    }
    res = holder.find_last_session(sess_spec_sent)
    if (type(res) is not dict) or ('produced' not in res):
        res = None
    if res:
        session_info = res

    sess_spec_received = {
        'feed_type': FEED_TYPE,
        'channels': {'$elemMatch': {'value': 'received'}},
        'authors': {'authority': 'telco', 'identifiers': {'type': 'phone_number', 'value': phone_number}}
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

def get_sms_configuration():

    sms_config = {
        'sms_gateway_url': None,
        'sms_gateway_key': None,
        'sms_session_duration': None,
        'sms_reply_send': None,
        'sms_reply_message': None,
        'sms_confirm_send': None,
        'sms_confirm_message': None,
    }

    for one_key in sms_config:
        one_value = get_config(one_key)
        if one_value is not None:
            sms_config[one_key] = one_value

    found_config = db[COLL_CONFIG].find_one({'_type': 'sms'})
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

