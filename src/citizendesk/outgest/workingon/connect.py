#!/usr/bin/env python
#
# Citizen Desk
#
'''
GET list of coverages:
/streams/workingon/reports/

'''

import os, sys, datetime, json
from bson import json_util
try:
    from flask import Blueprint, request, url_for
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.dbc import mongo_dbs
from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.outgest.workingon.utils import setup_config

def setup_blueprints(app, workingon_config_data):
    to_run = setup_config(workingon_config_data)
    if not to_run:
        return
    app.register_blueprint(workingon_reports_take)
    return

workingon_reports_take = Blueprint('bp_outgest_workingon_reports_take', __name__)

@workingon_reports_take.route('/streams/workingon/reports/', defaults={}, methods=['OPTIONS'], strict_slashes=False)
def take_workingon_reports_options():
    headers = {
        'Content-Type': 'text/plain; charset=utf-8',
        'Access-Control-Allow-Headers': 'X-Filter,X-HTTP-Method-Override,X-Format-DateTime,Authorization',
        'Access-Control-Allow-Origin': '*',
    }

    return ('', 200, headers)

@workingon_reports_take.route('/streams/workingon/reports/', defaults={}, methods=['GET'], strict_slashes=False)
def take_workingon_reports():

    from citizendesk.outgest.workingon import process

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

    try:
        res = process.get_workingon_reports_list(mongo_dbs.get_db().db, params['offset'], params['limit'], params['sort'])

        if not res[0]:
            ret_data = {'_meta': {'message': res[1]}}
            return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

        ret_data = {'_meta': {}, '_data': res[1]}
        if 2 < len(res):
            ret_data['_meta']['list'] = res[2]
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

    except Exception as exc:
        logger.warning('problem on workingon-oriented reports listing')
        return ('problem on workingon-oriented reports listing', 404,)
