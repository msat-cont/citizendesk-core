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
    from citizendesk.feeds.config import get_config

    logger = get_logger()
    client_ip = get_client_ip()

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
        recipients = data['recipients']
    except:
        return (json.dumps('provided data should contain "message", "recipients" parts'), 404, {'Content-Type': 'application/json'})

    searcher_url = get_config('sms_gateway_url')
    if ('sms_gateway_url' in data) and data['sms_gateway_url']:
        searcher_url = data['sms_gateway_url']

    res = process.do_post_send(mongo_dbs.get_db().db, sms_gateway_url, message, recipients)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

