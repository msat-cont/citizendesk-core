#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET
/feeds/twt/citizen/alias/id/<alias_value>
/feeds/twt/citizen/alias/name/<alias_value>

GET
/feeds/twt/citizen/alias/

POST
/feeds/twt/citizen/alias/id/<alias_value>
/feeds/twt/citizen/alias/name/<alias_value>
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

bp_feed_twt_citizen_alias = Blueprint('bp_feed_twt_citizen_alias', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_twt_citizen_alias)
    return

@bp_feed_twt_citizen_alias.route('/feeds/twt/citizen/alias/id/<alias_value>', defaults={'alias_type': 'alias_id'}, methods=['GET'], strict_slashes=False)
@bp_feed_twt_citizen_alias.route('/feeds/twt/citizen/alias/name/<alias_value>', defaults={'alias_type': 'alias_name'}, methods=['GET'], strict_slashes=False)
def feed_twt_citizen_alias_get_one(alias_type, alias_value):
    from citizendesk.feeds.twt.citizen_alias import process
    from citizendesk.feeds.config import get_config

    logger = get_logger()
    client_ip = get_client_ip()

    other = {'force': None}
    for key in other:
        if key in request.args:
            other[key] = request.args.get(key)

    force = False
    if other and ('force' in other):
        force = _get_boolean(other['force'])

    res = process.do_get_one(mongo_dbs.get_db().db, alias_type, alias_value)

    err_reason = None
    err_msg = None
    if not res[0]:
        err_msg = res[1]

    if (not res[0]) and force:
        err_msg = res[1]
        searcher_url = get_config('newstwister_url')
        res_aux = process.do_request_one(mongo_dbs.get_db().db, searcher_url, alias_type, alias_value)
        if not res_aux[0]:
            err_msg = res_aux[1]
            if 2 < len(res_aux):
                err_reason = res_aux[2]
        else:
            res = process.do_get_one(mongo_dbs.get_db().db, alias_type, alias_value)
            if not res[0]:
                err_msg = res_aux[1]
                err_reason = None

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': err_msg}}
        if err_reason:
            ret_data['_meta']['reason'] = err_reason
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_citizen_alias.route('/feeds/twt/citizen/alias/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_twt_citizen_alias_get_list():
    from citizendesk.feeds.twt.citizen_alias import process

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

@bp_feed_twt_citizen_alias.route('/feeds/twt/citizen/alias/id/<alias_value>/request/', defaults={'alias_type': 'alias_id'}, methods=['POST'], strict_slashes=False)
@bp_feed_twt_citizen_alias.route('/feeds/twt/citizen/alias/name/<alias_value>/request/', defaults={'alias_type': 'alias_name'}, methods=['POST'], strict_slashes=False)
def feed_twt_citizen_alias_request_one(alias_type, alias_value):
    from citizendesk.feeds.twt.citizen_alias import process
    from citizendesk.feeds.config import get_config

    logger = get_logger()
    client_ip = get_client_ip()

    searcher_url = get_config('newstwister_url')

    res = process.do_request_one(mongo_dbs.get_db().db, searcher_url, alias_type, alias_value)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        if 2 < len(res):
            ret_data['_meta']['reason'] = res[2]
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

