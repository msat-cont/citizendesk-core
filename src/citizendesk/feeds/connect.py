#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/twt/filter/
/feeds/twt/oauth/
/feeds/twt/stream/
/feeds/twt/endpoint/

'''

import os, sys, datetime, json
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.reporting.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.reporting.holder import ReportHolder

holder = ReportHolder()

bp_feed_twt_filter = Blueprint('bp_feed_twt_filter', __name__)

@bp_feed_twt_filter.route('/feed/twt/filter/<filter_id>', defaults={}, methods=['GET'], strict_slashes=False)
def feed_twt_filter(filter_id):
    from citizendesk.feeds import twt
    #.filter import do_get_one, schema

    logger = get_logger()
    client_ip = get_client_ip()

    '''
    allowed_ips = get_allowed_ips()
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: '+ str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))
    '''

    '''
    try:
        json_data = request.get_json(True, False, False)
    except:
        json_data = None

    if not json_data:
        logger.info('data not provided in the request')
        return ('Data not provided', 404,)
    for part in twt.filter.schema:
        if part not in json_data:
            logger.info('No ' + str(part) + ' provided')
            return ('No ' + str(part) + ' provided', 404,)
    '''

    res = twt.filter.do_get_one(holder, filter_id)

    return ('not yet implemented', 200,)

