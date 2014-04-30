#!/usr/bin/env python
#
# Citizen Desk
#
'''
GET list of coverages:
/outgest/liveblog/coverage/

GET list of published reports:
/outgest/liveblog/coverage/<coverage_id>/reports/published/

GET citizen info:
/outgest/liveblog/citizen/<citizen_id>/

'''

import os, sys, datetime, json
try:
    from flask import Blueprint, request, url_for
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips

def get_conf(name):
    config = {
    }

    if name in config:
        return config[name]
    return None

def setup_urls():
    coverages_url = url_for('.take_coverages')
    posts_url = url_for('.take_coverage_published_posts', coverage_id='<coverage_id>')
    set_config('coverages_url', coverages_url)
    set_config('posts_url', posts_url)

lb_coverage_take = Blueprint('lb_coverage_take', __name__)

@lb_coverage_take.route('/outgest/liveblog/coverage/', defaults={}, methods=['GET'], strict_slashes=False)
def take_coverages():

    try:
        res = get_coverage_list()
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200,)
    except Exception as exc:
        logger.warning('problem on liveblog-oriented coverages listing')
        return ('problem on liveblog-oriented coverages listing', 404,)

@lb_coverage_take.route('/outgest/liveblog/coverage/<coverage_id>/reports/published/', defaults={}, methods=['GET'], strict_slashes=False)
def take_coverage_published_posts(coverage_id):
    from citizendesk.ingest.twt.process import do_post

    logger = get_logger()
    client_ip = get_client_ip()

    allowed_ips = get_allowed_ips()
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed client from: '+ str(client_ip))
            return ('Client not allowed\n\n', 403,)
    logger.info('allowed client from: '+ str(client_ip))

    cid_last = request.args.get('cId')

    try:
        res = get_coverage_published_post_list(coverage_id, cid_last)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200,)
    except Exception as exc:
        logger.warning('problem on liveblog-oriented coverage reports listing')
        return ('problem on liveblog-oriented coverage reports listing', 404,)

@lb_coverage_take.route('/outgest/liveblog/citizen/<citizen_id>', defaults={}, methods=['GET'], strict_slashes=False)
def take_citizen(citizen_id):

    try:
        res = get_citizen(citizen_id)
        if (not res) or (not res[0]):
            logger.info(str(res[1]))
            return (res[1], 404,)
        return (json.dumps(res[1]), 200,)
    except Exception as exc:
        logger.warning('problem on liveblog-oriented citizen info retrieval')
        return ('problem on liveblog-oriented citizen info retrieval', 404,)

