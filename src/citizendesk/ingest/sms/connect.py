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
            logger.info('unallowed client from: '+ str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    params = {'feed': feed_name}
    for part in ['feed', 'phone', 'time', 'text']:
        if part not in params:
            params[part] = None
        if part in request.form:
            try:
                params[part] = str(request.form[part].encode('utf8'))
            except:
                pass

    timepoint = datetime.datetime.now()
    if not params['time']:
        params['time'] = timepoint

    for part in ['phone', 'text']:
        if not params[part]:
            return ('No ' + str(part) + ' provided', 404)

    try:
        res = do_post(db, params, client_ip)
        if not res[0]:
            logger.info(str(res[1]))
            return (res[1], 404,)
        return ('SMS received\n\n', 200,)
    except Exception as exc:
        logger.warning('problem on sms processing or saving')
        return ('problem on sms processing or saving', 404,)

