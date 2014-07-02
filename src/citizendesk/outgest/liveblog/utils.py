#!/usr/bin/env python
#
# Citizen Desk
#

LB_COVERAGE_BP_NAME = 'lb_coverage_take'

PUBLISHED_REPORTS_PLACEHOLDER = '__coverage_id_placeholder__'
REPORT_LINK_ID_PLACEHOLDER = '__report_link_id_placeholder__'

import os, sys, datetime, json, calendar
try:
    from flask import Blueprint, request, url_for
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

config = {
}

def get_conf(name):
    global config

    if name in config:
        return config[name]
    return None

def set_conf(key, value):
    global config

    config[key] = value

def setup_urls():
    coverages_url = url_for(LB_COVERAGE_BP_NAME + '.take_coverages')
    reports_url = url_for(LB_COVERAGE_BP_NAME + '.take_coverage_published_reports', coverage_id=PUBLISHED_REPORTS_PLACEHOLDER)
    author_url = url_for(LB_COVERAGE_BP_NAME + '.take_report_author', report_id=REPORT_LINK_ID_PLACEHOLDER, author_form='author')
    creator_url = url_for(LB_COVERAGE_BP_NAME + '.take_report_author', report_id=REPORT_LINK_ID_PLACEHOLDER, author_form='creator')

    set_conf('coverages_url', coverages_url)
    set_conf('reports_url', reports_url)
    set_conf('author_url', author_url)
    set_conf('creator_url', creator_url)

def update_from_cid(cid_got):
    update_ret = None

    try:
        if cid_got and cid_got.isdigit():
            cid_use = float(cid_got) / 1000000
            update_ret = datetime.datetime.utcfromtimestamp(cid_use)
    except:
        update_ret = None

    return update_ret

def cid_from_update(update_got):
    cid_ret = None

    try:
        cid_use = calendar.timegm(update_got.utctimetuple())
        cid_ret = (cid_use * 1000000) + update_got.microsecond
    except:
        cid_ret = None

    return cid_ret

