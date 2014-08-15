#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET
/feeds/img/service/
/feeds/img/service/id/<service_id>/

GET
/feeds/img/service/resolved/report/<report_id>/

POST
/feeds/img/service/
/feeds/img/service/id/<service_id>/activate/
/feeds/img/service/id/<service_id>/deactivate/

DELETE
/feeds/img/service/id/<service_id>/

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

bp_feed_img_service = Blueprint('bp_feed_img_service', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_img_service)
    return

@bp_feed_img_service.route('/feeds/img/service/resolved/report/<report_id>/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_img_service_get_resolved(report_id):
    from citizendesk.feeds.img.service import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_resolved(mongo_dbs.get_db().db, report_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    if 2 < len(res):
        ret_data['_meta']['list'] = res[2]
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_img_service.route('/feeds/img/service/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_img_service_get_list():
    from citizendesk.feeds.img.service import process

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

@bp_feed_img_service.route('/feeds/img/service/id/<service_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_img_service_get_one(service_id):
    from citizendesk.feeds.img.service import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_one(mongo_dbs.get_db().db, service_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_img_service.route('/feeds/img/service/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_img_service_insert_one():
    from citizendesk.feeds.img.service import process

    logger = get_logger()
    client_ip = get_client_ip()

    service_data = {}

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
        service_data['key'] = data['key']
        service_data['site'] = data['site']
        service_data['title'] = data['title']
        service_data['description'] = data['description']
        service_data['type'] = data['type']
        service_data['spec'] = data['spec']
    except:
        return (json.dumps('provided data should contain "key", "title", "description", "site", "type", "spec" parts'), 404, {'Content-Type': 'application/json'})

    if 'notice' in data:
        service_data['notice'] = str(data['notice'])
    if 'active' in data:
        service_data['active'] = _get_boolean(data['active'])

    res = process.do_insert_one(mongo_dbs.get_db().db, service_data)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_img_service.route('/feeds/img/service/id/<service_id>/activate/', defaults={'set_active': True}, methods=['POST'], strict_slashes=False)
@bp_feed_img_service.route('/feeds/img/service/id/<service_id>/deactivate/', defaults={'set_active': False}, methods=['POST'], strict_slashes=False)
def feed_img_service_activate_one(service_id, set_active):
    from citizendesk.feeds.img.service import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_set_active_one(mongo_dbs.get_db().db, service_id, set_active)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_img_service.route('/feeds/img/service/id/<service_id>/', defaults={}, methods=['DELETE'], strict_slashes=False)
def feed_img_service_delete_one(service_id):
    from citizendesk.feeds.img.service import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_delete_one(mongo_dbs.get_db().db, service_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})
