#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime#, logging
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.common.holder import ReportHolder

holder = ReportHolder()

from citizendesk.ingest.sms.sms_replier import send_sms

def get_conf(name):
    config = {
        'feed_type': 'SMS',
        'feed_conn': 'SMS',
        'time_delay': 1800,
        'send_config_path': '/opt/citizendesk/etc/citizendesk/send_sms.conf' # this should be set via startup params
    }

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

def get_sms():
    return None

sms_take = Blueprint('sms_take', __name__)

@sms_take.route('/sms_feeds/', methods=['GET', 'POST'])
def take_sms():
    from citizendesk.ingest.sms.process import do_post

    logger = get_logger()
    client_ip = get_client_ip()

    allowed_ips = get_allowed_ips()
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: '+ str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    params = {}
    for part in ['feed', 'phone', 'time', 'text']:
        params[part] = None
        if part in request.form:
            try:
                params[part] = str(request.form[part].encode('utf8'))
            except:
                pass
    '''
    sys.stderr.write(str(request.form) + '\n\n')
    save_list = []
    for part in ['feed', 'phone', 'time', 'text']:
        if part in request.form:
            save_list += [part + ': ' + str(request.form[part].encode('utf8'))]
    save_str = ', '.join(save_list) + '\n'
    sf = open('/tmp/cd.debug.001', 'a')
    sf.write(save_str)
    sf.close()
    '''

    for part in ['feed', 'phone', 'text']:
        if not params[part]:
            return ('No ' + str(part) + ' provided', 404)

    if not params['time']:
        params['time'] = datetime.datetime.now()

    try:
        res = do_post(holder, params, client_ip)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return ('SMS received\n\n', 200,)
    except Exception as exc:
        logger.warning('problem on tweet processing or saving')
        return ('problem on tweet processing or saving', 404,)

