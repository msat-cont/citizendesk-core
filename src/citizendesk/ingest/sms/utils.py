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

DEFAULT_TIME_DELAY = 1800

def load_send_sms_config(config_path):
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

    if (not 'send_reply' in config_data) or (not config_data['send_reply']):
        return False

    if ('time_delay' in config_data) and (config_data['time_delay']):
        try:
            time_delay = 60 * int(config_data['time_delay'])
            set_conf('time_delay', time_delay)
        except:
            pass

    if 'reply_message' in config_data:
        reply_message = config_data['reply_message']
        set_conf('reply_message', reply_message)

    send_config = {}
    for param in ['method', 'url', 'phone_param', 'text_param']:
        send_config[param] = None
        if (param in config_data) and config_data[param]:
            send_config[param] = config_data[param]
    set_conf('send_config', send_config)

    set_conf('send_reply', True)

config = {
    'feed_type': 'SMS',
    'publisher': 'sms_gateway',
    'send_reply': False,
    'reply_message': None,
    'time_delay': DEFAULT_TIME_DELAY,
    'send_config': None
}

def set_conf(name, value):
    global config

    config[name] = value

def get_conf(name):
    global config

    if name in config:
        return config[name]
    return None

def gen_id(feed_type, citizen):

    rnd_list = [str(hex(i))[-1:] for i in range(16)]
    random.shuffle(rnd_list)
    id_value = '' + feed_type + ':' + citizen
    id_value += ':' + datetime.datetime.now().isoformat()
    id_value += ':' + ''.join(rnd_list)
    return id_value

def get_sms(channel_type, phone_number):
    FEED_TYPE = get_conf('feed_type')

    sess_spec = {'feed_type': FEED_TYPE, 'channels': {'$elemMatch': {'type': channel_type, 'value': phone_number}}}
    return holder.find_last_session(sess_spec)

