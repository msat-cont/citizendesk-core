#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET
/feeds/err/ingest/

POST
/feeds/err/ingest/<notice_timestamp>

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

bp_feed_err_ingest = Blueprint('bp_feed_err_ingest', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_err_ingest)
    return

@bp_feed_err_ingest.route('/feeds/err/ingest/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_err_ingest_get_list():
    from citizendesk.feeds.err.ingest import process

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

    res = process.do_get_list(mongo_dbs.get_db().db, params['offset'], params['limit'], params['sort'], other)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    if 2 < len(res):
        ret_data['_meta']['list'] = res[2]
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_err_ingest.route('/feeds/err/ingest/<notice_timestamp>', defaults={}, methods=['POST'], strict_slashes=False)
def feed_err_ingest_insert_one(notice_timestamp):
    from citizendesk.feeds.err.ingest import process

    logger = get_logger()
    client_ip = get_client_ip()

    notice_data = {}

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
        notice_data['feed_type'] = data['feed_type']
        notice_data['channel'] = data['channel']
        notice_data['message'] = data['message']
    except:
        return (json.dumps('provided data should contain "feed_type", "channel", "message" parts'), 404, {'Content-Type': 'application/json'})

    res = process.do_insert_one(mongo_dbs.get_db().db, notice_timestamp, notice_data)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

