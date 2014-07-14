#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

POST
/feeds/any/report/id/<doc_id>/publish/
/feeds/any/report/id/<doc_id>/publish/<coverage_id>/
/feeds/any/report/id/<doc_id>/unpublish/
/feeds/any/report/id/<doc_id>/unpublish/<coverage_id>/

POST
/feeds/any/report/id/<doc_id>/on_behalf_of/
/feeds/any/report/id/<doc_id>/on_behalf_of/<user_id>/

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

bp_feed_any_report = Blueprint('bp_feed_any_report', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_any_report)
    return

@bp_feed_any_report.route('/feeds/any/report/id/<doc_id>/publish/', defaults={'coverage_id': None}, methods=['POST'], strict_slashes=False)
@bp_feed_any_report.route('/feeds/any/report/id/<doc_id>/publish/<coverage_id>/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_any_report_publish_one(doc_id, coverage_id):
    from citizendesk.feeds.any.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_publish_one(mongo_dbs.get_db().db, doc_id, coverage_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_any_report.route('/feeds/any/report/id/<doc_id>/unpublish/', defaults={'coverage_id': None}, methods=['POST'], strict_slashes=False)
@bp_feed_any_report.route('/feeds/any/report/id/<doc_id>/unpublish/<coverage_id>/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_any_report_unpublish_one(doc_id, coverage_id):
    from citizendesk.feeds.any.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_unpublish_one(mongo_dbs.get_db().db, doc_id, coverage_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})

@bp_feed_any_report.route('/feeds/any/report/id/<doc_id>/on_behalf_of/', defaults={'user_id': None}, methods=['POST'], strict_slashes=False)
@bp_feed_any_report.route('/feeds/any/report/id/<doc_id>/on_behalf_of/<user_id>/', defaults={}, methods=['POST'], strict_slashes=False)
def feed_any_report_on_behalf_of(doc_id, user_id):
    from citizendesk.feeds.any.report import process

    logger = get_logger()
    client_ip = get_client_ip()

    res = process.do_on_behalf_of(mongo_dbs.get_db().db, doc_id, user_id)

    if not res[0]:
        ret_data = {'_meta': {'schema': process.schema, 'message': res[1]}}
        return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 404, {'Content-Type': 'application/json'})

    ret_data = {'_meta': {'schema': process.schema}, '_data': res[1]}
    return (json.dumps(ret_data, default=json_util.default, sort_keys=True), 200, {'Content-Type': 'application/json'})
