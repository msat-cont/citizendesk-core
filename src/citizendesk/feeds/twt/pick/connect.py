#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

POST
/feeds/twt/pick/

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

bp_feed_twt_pick = Blueprint('bp_feed_twt_pick', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_twt_pick)
    return

@bp_feed_twt_pick.route('/feeds/twt/pick/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_twt_pick_one_post():
    from citizendesk.feeds.twt.pick import process
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
        endpoint_id = data['endpoint_id']
        tweet_spec = data['tweet_spec']
    except:
        return (json.dumps('provided data should contain "user_id", "endpoint_id", "tweet_spec" parts'), 404, {'Content-Type': 'application/json'})

    picker_url = get_config('newstwister_url')

    res = process.do_post_pick(mongo_dbs.get_db().db, picker_url, user_id, endpoint_id, tweet_spec)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})
