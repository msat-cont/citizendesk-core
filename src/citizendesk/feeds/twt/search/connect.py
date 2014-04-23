#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

POST, SEARCH
/feeds/twt/search/

POST, SEARCH
/feeds/twt/search/<user_id>/request/<request_id>/

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

bp_feed_twt_search = Blueprint('bp_feed_twt_search', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_twt_search)
    return

@bp_feed_twt_search.route('/feeds/twt/search/', defaults={}, methods=['POST', 'SEARCH'], strict_slashes=False)
def feed_twt_search_one_post():
    from citizendesk.feeds.twt.search import process
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
        user_id = data['user_id']
        request_id = data['request_id']
        search_spec = data['search_spec']
    except:
        return (json.dumps('provided data should contain "user_id", "request_id", "search_spec" parts'), 404, {'Content-Type': 'application/json'})

    searcher_url = get_config('newstwister_url')
    if ('searcher_url' in data) and data['searcher_url']:
        searcher_url = data['searcher_url']

    res = process.do_post_search(mongo_dbs.get_db().db, searcher_url, user_id, request_id, search_spec)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_twt_search.route('/feeds/twt/search/<user_id>/request/<request_id>/', defaults={}, methods=['POST', 'SEARCH'], strict_slashes=False)
def feed_twt_search_one_search(user_id, request_id):
    from citizendesk.feeds.twt.search import process
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

    searcher_url = get_config('newstwister_url')

    res = process.do_post_search(mongo_dbs.get_db().db, searcher_url, user_id, request_id, data)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

