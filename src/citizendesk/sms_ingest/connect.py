#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, subprocess, logging
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.reporting.holder import ReportHolder
holder = ReportHolder()

def get_conf(name):
    config = {'feed_type':'SMS', 'feed_conn':'Gammu', 'time_delay':1800}
    config['send_script_path'] = '/opt/gammu/bin/send_sms.py'
    config['send_config_path'] = '/opt/gammu/etc/gammu/send_sms.conf'
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

def within_session(last_received, current_received):
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
    send_script = get_conf('send_script_path')
    send_config = get_conf('send_config_path')
    try:
        subprocess.call([send_script, send_config, phone_number, message, unicode_flag])
    except:
        logging.error('can not send SMS to: ' + str(phone_number))
        return False

    return True

sms_take = Blueprint('sms_take', __name__)

@sms_take.route('/sms_feeds/', methods=['GET', 'POST'])
def take_sms():
    params = {}
    for part in ['feed', 'phone', 'time', 'text']:
        params[part] = None
        if part in request.form:
            params[part] = str(request.form[part].encode('utf8'))
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

    for part in ['feed', 'phone', 'time', 'text']:
        if not params[part]:
            return (404, 'No ' + str(part) + ' provided')

    feed_name = params['feed']
    phone_number = params['phone']

    feed_type = get_conf('feed_type')
    received = params[time]
    if not received:
        received = datetime.datetime.now()

    channels = [{'type':'SMS', 'value':feed_name}]
    publishers = []
    authors = [{'type':'phone', 'value':phone_number}]
    endorsers = []

    original = params[text]
    texts = [params[text]]
    tags = []
    if params[text]:
        for word in params[text].split(' '):
            if word.startswith('#'):
                use_tag = word[1:]
                if use_tag:
                    tags.append(use_tag)

    # session_id should only be set here when reusing an old one
    session = None
    new_session = True

    session_look_spec = {'channel': {'type':channels[0]['type']}, 'author':authors[0]}
    force_new_session = holder.get_force_new_session(session_look_spec)
    if force_new_session:
        holder.clear_force_new_session(session_look_spec, True)
    else:
        last_report = holder.find_last_session({'channels':channels[0], 'authors':authors[0]})
        if last_report:
            if within_session(last_report['received'], received):
                session = last_report['session']
                new_session = False

    report = {}
    report['report_id'] = gen_id(feed_type, phone_number)
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

