#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, random
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.ingest.sms.utils import get_sms_configuration

bp_ingest_sms_feed = Blueprint('bp_ingest_sms_feed', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_ingest_sms_feed)
    return

@bp_ingest_sms_feed.route('/ingest/sms/feed/', defaults={'feed_name': None}, methods=['GET', 'POST'], strict_slashes=False)
@bp_ingest_sms_feed.route('/ingest/sms/feed/<feed_name>', defaults={}, methods=['GET', 'POST'], strict_slashes=False)
def ingest_sms_feed_take_one(feed_name):
    from citizendesk.common.dbc import mongo_dbs
    db = mongo_dbs.get_db().db

    from citizendesk.ingest.sms.process import do_post

    logger = get_logger()
    client_ip = get_client_ip()

    allowed_ips = get_allowed_ips()
    if (allowed_ips is not None) and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: ' + str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    store_keys = {
        'phone': 'phone_param',
        'text': 'text_param',
        'feed': 'feed_param',
        'time': 'time_param',
        'pass': 'pass_param',
    }
    param_keys = {}
    for key in store_keys:
        param_keys[store_keys[key]] = key

    main_config = get_sms_configuration(db)
    sms_password_key = main_config['sms_password_key']

    for key in param_keys:
        take_key = 'sms_' + key
        if take_key in main_config:
            param_keys[key] = main_config[take_key]

    params = {'feed': feed_name}
    for store_key in store_keys:
        part_key = store_keys[store_key]
        part_param = param_keys[part_key]
        if store_key not in params:
            params[store_key] = None
        if part_param in request.args:
            try:
                params[store_key] = str(request.args[part_param].encode('utf8'))
            except:
                pass
        if part_param in request.form:
            try:
                params[store_key] = str(request.form[part_param].encode('utf8'))
            except:
                pass

    timepoint = datetime.datetime.now()
    if params['time']:
        try:
            dt_format = '%Y-%m-%dT%H:%M:%S'
            if '.' in params['time']:
                dt_format = '%Y-%m-%dT%H:%M:%S.%f'
            params['time'] = datetime.datetime.strptime(params['time'], dt_format)
        except:
            params['time'] = None
    if not params['time']:
        params['time'] = timepoint

    for part in ['phone', 'text']:
        if not params[part]:
            return ('No ' + str(part) + ' provided', 404)

    if sms_password_key:
        if sms_password_key != params['pass']:
            logger.info('request with wrong pass-phrase from: ' + str(client_ip))
            return ('wrong pass-phrase\n\n', 403,)

    try:
        res = do_post(db, params, main_config, client_ip)
        if not res[0]:
            logger.info(str(res[1]))
            return (res[1], 404,)
        return ('SMS received\n\n', 200,)
    except Exception as exc:
        logger.warning('problem on sms processing or saving')
        return ('problem on sms processing or saving', 404,)

