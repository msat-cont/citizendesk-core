#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

POST
/feeds/sms/send/

'''

import os, sys, datetime, json
from bson import json_util
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.common.dbc import mongo_dbs

bp_feed_sms_send = Blueprint('bp_feed_sms_send', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_sms_send)
    return

@bp_feed_sms_send.route('/feeds/sms/send/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_sms_send_one_post():
    from citizendesk.feeds.sms.send import process
    from citizendesk.feeds.config import get_config as get_main_config

    sms_allowed_ips = get_main_config('sms_allowed_ips')
    sms_gateway_url = get_main_config('sms_gateway_url')
    sms_gateway_key = get_main_config('sms_gateway_key')
    try:
        sms_gateway_api = get_main_config('sms_gateway_api')
    except:
        sms_gateway_api = 'frontlinesms'

    logger = get_logger()
    client_ip = get_client_ip()
    if (sms_allowed_ips is not None) and ('*' not in sms_allowed_ips):
        if not client_ip in sms_allowed_ips:
            logger.info('unallowed sms-send request from: ' + str(client_ip))
            return (json.dumps('client not allowed'), 403, {'Content-Type': 'application/json'})

    try:
        data = request.get_json(True, False, False)
        if type(data) is not dict:
            data = None
    except:
        data = None
    if data is None:
        try:
            data = request.json
            if type(data) is not dict:
                data = None
        except:
            data = None
    if data is None:
        return (json.dumps('provided data are not valid json'), 404, {'Content-Type': 'application/json'})

    try:
        message = data['message']
        targets = data['targets']
        user_id = data['user_id']
    except:
        return (json.dumps('provided data should contain "message", "targets", "user_id" parts'), 404, {'Content-Type': 'application/json'})

    language = None
    sensitive = None
    if 'language' in data:
        language = data['language']
    if 'sensitive' in data:
        sensitive = data['sensitive']

    if ('control' in data) and (type(data['control']) is dict):
        control = data['control']
        if ('sms_gateway_url' in control) and control['sms_gateway_url']:
            sms_gateway_url = control['sms_gateway_url']
        if ('sms_gateway_key' in control) and control['sms_gateway_key']:
            sms_gateway_key = control['sms_gateway_key']

    res = process.do_post_send(mongo_dbs.get_db().db, sms_gateway_api, sms_gateway_url, sms_gateway_key, message, targets, user_id, language, sensitive, client_ip)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        if 2 < len(res):
            ret_data['_meta']['reason'] = res[2]
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

