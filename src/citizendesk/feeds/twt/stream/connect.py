#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

GET, POST
/feeds/twt/stream/

GET, PUT, PATCH, DELETE
/feeds/twt/stream/<stream_id>/

POST
/feeds/twt/stream/<stream_id>/start

POST
/feeds/twt/stream/<stream_id>/stop

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

bp_feed_twt_stream = Blueprint('bp_feed_twt_stream', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_twt_stream)
    return

@bp_feed_twt_stream.route('/feeds/twt/stream/<stream_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_twt_stream_get_one(stream_id):
    from citizendesk.feeds.twt.stream import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_get_one(mongo_dbs.get_db().db, stream_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_stream.route('/feeds/twt/stream/', defaults={}, methods=['GET'], strict_slashes=False)
def feed_twt_stream_get_list():
    from citizendesk.feeds.twt.stream import process

    logger = get_logger()
    client_ip = get_client_ip()

    params = {'offset': None, 'limit': None}
    for key in params:
        if key in request.args:
            try:
                params[key] = int(request.args.get(key))
            except:
                params[key] = None

    res = process.do_get_list(mongo_dbs.get_db().db, params['offset'], params['limit'])

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    if 2 < len(res):
        ret_data['_meta']['list'] = res[2]
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_stream.route('/feeds/twt/stream/', defaults={'stream_id': None}, methods=['POST'], strict_slashes=False)
@bp_feed_twt_stream.route('/feeds/twt/stream/<stream_id>', defaults={}, methods=['PUT'], strict_slashes=False)
def feed_twt_stream_post_one(stream_id):
    from citizendesk.feeds.twt.stream import process

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

    res = process.do_post_one(mongo_dbs.get_db().db, stream_id, data)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_stream.route('/feeds/twt/stream/<stream_id>/start', defaults={'switch_on':True}, methods=['POST'], strict_slashes=False)
@bp_feed_twt_stream.route('/feeds/twt/stream/<stream_id>/stop', defaults={'switch_on':False}, methods=['POST'], strict_slashes=False)
def feed_twt_stream_patch_one_emulate(stream_id, switch_on):
    from citizendesk.feeds.twt.stream import process
    from citizendesk.feeds.config import get_config

    logger = get_logger()
    client_ip = get_client_ip()

    data = {
        'control': {
            'streamer_url': get_config('newstwister_url'),
            'switch_on': switch_on
        },
    }

    params = {'force': True}

    res = process.do_patch_one(mongo_dbs.get_db().db, stream_id, data, params['force'])

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_stream.route('/feeds/twt/stream/<stream_id>', defaults={}, methods=['PATCH'], strict_slashes=False)
def feed_twt_stream_patch_one(stream_id):
    from citizendesk.feeds.twt.stream import process
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

    if ('streamer_url' not in data) or (not data['streamer_url']):
        data['streamer_url'] = get_config('newstwister_url')

    params = {'force': None}
    for key in params:
        if key in request.args:
            params[key] = request.args.get(key)

    res = process.do_patch_one(mongo_dbs.get_db().db, stream_id, data, params['force'])

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_stream.route('/feeds/twt/stream/<stream_id>', defaults={}, methods=['DELETE'], strict_slashes=False)
def feed_twt_stream_delete_one(stream_id):
    from citizendesk.feeds.twt.stream import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_delete_one(mongo_dbs.get_db().db, stream_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

