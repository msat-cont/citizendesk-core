#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, random, json
from bson import json_util
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips

bp_ingest_url_feed = Blueprint('bp_ingest_url_feed', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_ingest_url_feed)
    return

@bp_ingest_url_feed.route('/ingest/url/feed/', defaults={'feed_name': None}, methods=['POST'], strict_slashes=False)
@bp_ingest_url_feed.route('/ingest/url/feed/<feed_name>', defaults={}, methods=['POST'], strict_slashes=False)
def ingest_url_feed_take_one(feed_name):
    from citizendesk.common.dbc import mongo_dbs
    db = mongo_dbs.get_db().db

    from citizendesk.ingest.url.process import do_post

    logger = get_logger()
    client_ip = get_client_ip()

    allowed_ips = get_allowed_ips()
    if (allowed_ips is not None) and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: ' + str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    param_keys = [
        'feed_name',
        'url_link',
        'request_id',
    ]
    params = {'feed_name': feed_name}

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

    for one_param in param_keys:
        if one_param in data:
            try:
                params[one_param] = str(data[one_param].encode('utf8'))
            except:
                pass

    for one_param in param_keys:
        if (not one_param in params) or (not params[one_param]):
            return ('No ' + str(one_param) + ' provided', 404)

    try:
        res = do_post(db, params['url_link'], params['feed_name'], params['request_id'], client_ip)
        if not res[0]:
            logger.info(str(res[1]))
            return (res[1], 404,)
        ret_data = res[1]
        return json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'}

    except Exception as exc:
        logger.warning('problem on url processing or saving: ' + str(exc))
        return ('problem on url processing or saving: ' + str(exc), 404,)

