#!/usr/bin/env python
#
# Citizen Desk
#
'''
GET list of coverages:
/streams/workingon/reports/

'''

import os, sys, datetime, json
try:
    from flask import Blueprint, request, url_for
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.dbc import mongo_dbs
from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.outgest.workingon.utils import WORKINGON_REPORT_FIELD_NAME
from citizendesk.outgest.workingon.utils import setup_urls, setup_config

def setup_blueprints(app, lb_config_data):
    setup_config(lb_config_data)
    app.register_blueprint(lb_coverage_take)
    return

workingon_reports_take = Blueprint(WORKINGON_REPORTS_BP_NAME, __name__)

@workingon_reports_take.route('/streams/workingon/reports/', defaults={}, methods=['OPTIONS'], strict_slashes=False)
def take_workingon_reports_options():
    headers = {
        'Content-Type': 'text/plain; charset=utf-8',
        'Access-Control-Allow-Headers': 'X-Filter,X-HTTP-Method-Override,X-Format-DateTime,Authorization',
        'Access-Control-Allow-Origin': '*',
    }

    return ('', 200, headers)

@lb_coverage_take.route('/streams/workingon/reports/', defaults={}, methods=['GET'], strict_slashes=False)
def take_workingon_reports():
    setup_urls()

    from citizendesk.outgest.workingon.process import get_workingon_reports_list

    logger = get_logger()
    client_ip = get_client_ip()

    try:
        res = get_workingon_reports_list(mongo_dbs.get_db().db)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})
    except Exception as exc:
        logger.warning('problem on workingon-oriented reports listing')
        return ('problem on workingon-oriented reports listing', 404,)
