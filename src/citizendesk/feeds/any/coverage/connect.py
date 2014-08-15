#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET
/feeds/any/coverage/
/feeds/any/coverage/id/<coverage_id>/

POST
/feeds/any/coverage/
/feeds/any/coverage/id/<coverage_id>/activate/
/feeds/any/coverage/id/<coverage_id>/deactivate/

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

bp_feed_any_coverage = Blueprint('bp_feed_any_coverage', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_any_coverage)
    return

@bp_feed_any_coverage.route('/feeds/any/coverage/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_any_coverage_get_list():
    from citizendesk.feeds.any.coverage import process

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

    other = {'name_only': None}
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

@bp_feed_any_coverage.route('/feeds/any/coverage/id/<coverage_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_any_coverage_get_one(coverage_id):
    from citizendesk.feeds.any.coverage import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_one(mongo_dbs.get_db().db, coverage_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_any_coverage.route('/feeds/any/coverage/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_any_coverage_insert_one():
    from citizendesk.feeds.any.coverage import process

    logger = get_logger()
    client_ip = get_client_ip()

    coverage_data = {}

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
        coverage_data['title'] = data['title']
        coverage_data['description'] = data['description']
        coverage_data['user_id'] = data['user_id']
    except:
        return (json.dumps('provided data should contain "title", "description", "user_id" parts'), 404, {'Content-Type': 'application/json'})

    if 'active' in data:
        coverage_data['active'] = _get_boolean(data['active'])

    res = process.do_insert_one(mongo_dbs.get_db().db, coverage_data)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_any_coverage.route('/feeds/any/coverage/id/<coverage_id>/activate/', defaults={'set_active': True}, methods=['POST'], strict_slashes=False)
@bp_feed_any_coverage.route('/feeds/any/coverage/id/<coverage_id>/deactivate/', defaults={'set_active': False}, methods=['POST'], strict_slashes=False)
def feed_any_coverage_activate_one(coverage_id, set_active):
    from citizendesk.feeds.any.coverage import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_set_active_one(mongo_dbs.get_db().db, coverage_id, set_active)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

