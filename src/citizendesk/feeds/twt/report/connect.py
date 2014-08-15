#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET, PATCH,
/feeds/twt/report/<report_id>/

GET
/feeds/twt/endpoint/stream/<endpoint_id>/
/feeds/twt/endpoint/search/<endpoint_id>/

GET
/feeds/twt/endpoint/stream/<endpoint_id>/proto/<is_proto>/
/feeds/twt/endpoint/search/<endpoint_id>/proto/<is_proto>/

GET
/feeds/twt/session/<session_id>/

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

bp_feed_twt_report = Blueprint('bp_feed_twt_report', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_twt_report)
    return

@bp_feed_twt_report.route('/feeds/twt/report/<report_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_twt_report_get_one(report_id):
    from citizendesk.feeds.twt.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_one(mongo_dbs.get_db().db, report_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_report.route('/feeds/twt/endpoint/stream/<endpoint_id>', defaults={'endpoint_type': 'stream', 'is_proto': None}, methods=['GET'], strict_slashes=False)
@bp_feed_twt_report.route('/feeds/twt/endpoint/stream/<endpoint_id>/proto/<is_proto>', defaults={'endpoint_type': 'stream'}, methods=['GET'], strict_slashes=False)
@bp_feed_twt_report.route('/feeds/twt/endpoint/search/<endpoint_id>', defaults={'endpoint_type': 'search', 'is_proto': None}, methods=['GET'], strict_slashes=False)
@bp_feed_twt_report.route('/feeds/twt/endpoint/search/<endpoint_id>/proto/<is_proto>', defaults={'endpoint_type': 'search'}, methods=['GET'], strict_slashes=False)
def feed_twt_report_get_list(endpoint_type, endpoint_id, is_proto):
    from citizendesk.feeds.twt.report import process

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

    res = process.do_get_list(mongo_dbs.get_db().db, endpoint_type, endpoint_id, is_proto, params['offset'], params['limit'], params['sort'], other)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    if 2 < len(res):
        ret_data['_meta']['list'] = res[2]
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_report.route('/feeds/twt/session/<session_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_twt_report_get_session(session_id):
    from citizendesk.feeds.twt.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    params = {'offset': None, 'limit': None}
    for key in params:
        if key in request.args:
            try:
                params[key] = int(request.args.get(key))
            except:
                params[key] = None

    res = process.do_get_session(mongo_dbs.get_db().db, session_id, params['offset'], params['limit'])

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    if 2 < len(res):
        ret_data['_meta']['list'] = res[2]
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_report.route('/feeds/twt/report/<report_id>', defaults={}, methods=['PATCH'], strict_slashes=False)
def feed_twt_report_patch_one(report_id):
    from citizendesk.feeds.twt.report import process

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

    res = process.do_patch_one(mongo_dbs.get_db().db, report_id, data)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

