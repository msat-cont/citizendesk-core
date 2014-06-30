#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET
/feeds/sms/report/id/<doc_id>

GET
/feeds/sms/report/
/feeds/sms/report/session/<session_id>
/feeds/sms/report/sent_to/<phone_number>
/feeds/sms/report/received_from/<phone_number>
'''

import os, sys, datetime, json
from bson import json_util
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.dbc import mongo_dbs

bp_feed_sms_report = Blueprint('bp_feed_sms_report', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_sms_report)
    return

@bp_feed_sms_report.route('/feeds/sms/report/id/<doc_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_sms_report_get_one(doc_id):
    from citizendesk.feeds.sms.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_one(mongo_dbs.get_db().db, doc_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_sms_report.route('/feeds/sms/report/', defaults={'value_id':None, 'value_type':None}, methods=['GET'], strict_slashes=False)
@bp_feed_sms_report.route('/feeds/sms/report/session/<value_id>', defaults={'value_type':'session_id'}, methods=['GET'], strict_slashes=False)
@bp_feed_sms_report.route('/feeds/sms/report/sent_to/<value_id>', defaults={'value_type':'sent_to'}, methods=['GET'], strict_slashes=False)
@bp_feed_sms_report.route('/feeds/sms/report/received_from/<value_id>', defaults={'value_type':'received_from'}, methods=['GET'], strict_slashes=False)
def feed_sms_report_get_list(value_type, value_id):
    from citizendesk.feeds.sms.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    params = {'offset': None, 'limit': None}
    for key in params:
        if key in request.args:
            try:
                params[key] = int(request.args.get(key))
            except:
                params[key] = None
    for key in ['sort']:
        params[key] = None
        if key in request.args:
            params[key] = request.args.get(key)

    other = {'text_only': None}
    for key in other:
        if key in request.args:
            other[key] = request.args.get(key)

    res = process.do_get_list(mongo_dbs.get_db().db, value_type, value_id, params['offset'], params['limit'], params['sort'], other)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    if 3 >= len(res):
        ret_data['_meta']['list'] = res[2]
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

