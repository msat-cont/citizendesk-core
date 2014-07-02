#!/usr/bin/env python
#
# Citizen Desk
#
'''
GET list of coverages:
/outgest/liveblog/coverage/

GET list of published reports:
/outgest/liveblog/coverage/<coverage_id>/reports/published/

GET report author info:
/outgest/liveblog/report/<report_id>/author/
/outgest/liveblog/report/<report_id>/creator/

'''

import os, sys, datetime, json
try:
    from flask import Blueprint, request, url_for
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.dbc import mongo_dbs
from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.outgest.liveblog.utils import LB_COVERAGE_BP_NAME
from citizendesk.outgest.liveblog.utils import get_conf, set_conf, update_from_cid, setup_urls

PUBLISHED_REPORTS_SUFFIX = 'reports/published/'

def setup_blueprints(app):
    app.register_blueprint(lb_coverage_take)
    return

lb_coverage_take = Blueprint(LB_COVERAGE_BP_NAME, __name__)

@lb_coverage_take.route('/outgest/liveblog/coverage/', defaults={}, methods=['GET'], strict_slashes=False)
def take_coverages():
    setup_urls()

    from citizendesk.outgest.liveblog.process import get_coverage_list

    logger = get_logger()
    client_ip = get_client_ip()

    try:
        res = get_coverage_list(mongo_dbs.get_db().db)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200,)
    except Exception as exc:
        logger.warning('problem on liveblog-oriented coverages listing')
        return ('problem on liveblog-oriented coverages listing', 404,)

@lb_coverage_take.route('/outgest/liveblog/coverage/<coverage_id>/' + PUBLISHED_REPORTS_SUFFIX, defaults={}, methods=['GET'], strict_slashes=False)
def take_coverage_published_reports(coverage_id):
    setup_urls()

    from citizendesk.outgest.liveblog.process import get_coverage_published_report_list

    logger = get_logger()
    client_ip = get_client_ip()

    cid_last = request.args.get('cId.since')
    update_last = update_from_cid(cid_last)

    try:
        res = get_coverage_published_report_list(mongo_dbs.get_db().db, coverage_id, update_last)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200,)
    except Exception as exc:
        logger.warning('problem on liveblog-oriented coverage reports listing')
        return ('problem on liveblog-oriented coverage reports listing', 404,)

@lb_coverage_take.route('/outgest/liveblog/report/<report_id>/author/', defaults={'author_form': 'author'}, methods=['GET'], strict_slashes=False)
@lb_coverage_take.route('/outgest/liveblog/report/<report_id>/creator/', defaults={'author_form': 'creator'}, methods=['GET'], strict_slashes=False)
def take_report_author(report_id, author_form):
    setup_urls()

    from citizendesk.outgest.liveblog.process import get_report_author

    logger = get_logger()
    client_ip = get_client_ip()

    try:
        res = get_report_author(mongo_dbs.get_db().db, report_id, author_form)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200,)
    except Exception as exc:
        logger.warning('problem on liveblog-oriented citizen info retrieval')
        return ('problem on liveblog-oriented citizen info retrieval', 404,)

