#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET
/feeds/sms/citizen/alias/id/<alias_id>
/feeds/sms/citizen/alias/phone_number/<phone_number>

GET
/feeds/sms/citizen/alias/

POST
/feeds/sms/citizen/alias/

PUT
/feeds/sms/citizen/alias/id/<alias_id>
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

bp_feed_sms_citizen_alias = Blueprint('bp_feed_sms_citizen_alias', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_sms_citizen_alias)
    return

@bp_feed_sms_citizen_alias.route('/feeds/sms/citizen/alias/id/<alias_value>', defaults={'alias_type': 'alias_id'}, methods=['GET'], strict_slashes=False)
@bp_feed_sms_citizen_alias.route('/feeds/sms/citizen/alias/phone_number/<alias_value>', defaults={'alias_type': 'phone_number'}, methods=['GET'], strict_slashes=False)
def feed_sms_citizen_alias_get_one(alias_type, alias_value):
    from citizendesk.feeds.sms.citizen_alias import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_one(mongo_dbs.get_db().db, alias_type, alias_value)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_sms_citizen_alias.route('/feeds/sms/citizen/alias/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_sms_citizen_alias_get_list():
    from citizendesk.feeds.sms.citizen_alias import process

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

@bp_feed_sms_citizen_alias.route('/feeds/sms/citizen/alias/', defaults={'alias_id': None}, methods=['POST'], strict_slashes=False)
@bp_feed_sms_citizen_alias.route('/feeds/sms/citizen/alias/id/<alias_id>/', defaults={}, methods=['PUT'], strict_slashes=False)
def feed_sms_citizen_alias_post_one(alias_id):
    from citizendesk.feeds.sms.citizen_alias import process

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
        alias_spec = data['spec']
        user_id = data['user_id']
    except:
        return (json.dumps('provided data should contain "spec", "user_id" parts'), 404, {'Content-Type': 'application/json'})

    if not alias_id:
        if ('_id' in data) and (data['_id']):
            alias_id = data['_id']

    res = process.do_post_one(mongo_dbs.get_db().db, alias_id, alias_spec, user_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        if 2 < len(res):
            ret_data['_meta']['reason'] = res[2]
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

