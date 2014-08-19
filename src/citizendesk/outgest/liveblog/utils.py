#!/usr/bin/env python
#
# Citizen Desk
#

LB_COVERAGE_BP_NAME = 'bp_outgest_lb_coverage_take'

COVERAGE_PLACEHOLDER = '__coverage_id_placeholder__'
PUBLISHED_REPORTS_PLACEHOLDER = '__coverage_id_placeholder__'
REPORT_LINK_ID_PLACEHOLDER = '__report_link_id_placeholder__'

import os, sys, datetime, json, calendar

try:
    long
except:
    long = int

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

def setup_config(liveblog_config_data):
    if type(liveblog_config_data) is not dict:
        return

    use_keys = [
        'default_report_author_name',
        'default_report_author_icon',
        'default_report_author_uuid',
        'sms_report_creator_name',
        'sms_report_creator_icon',
        'sms_report_creator_uuid',
    ]

    for one_key in use_keys:
        if (one_key in liveblog_config_data) and liveblog_config_data[one_key]:
            set_conf(one_key, liveblog_config_data[one_key])

def setup_urls():
    request_host = 'localhost'
    if request.host:
        request_host = str(request.host)
    start = '//' + request_host

    coverages_url = url_for(LB_COVERAGE_BP_NAME + '.take_coverages')
    coverage_info_url = url_for(LB_COVERAGE_BP_NAME + '.take_coverage_info', coverage_id=COVERAGE_PLACEHOLDER)
    reports_url = url_for(LB_COVERAGE_BP_NAME + '.take_coverage_published_reports', coverage_id=PUBLISHED_REPORTS_PLACEHOLDER)
    author_url = url_for(LB_COVERAGE_BP_NAME + '.take_report_author', report_id=REPORT_LINK_ID_PLACEHOLDER, author_form='author')
    creator_url = url_for(LB_COVERAGE_BP_NAME + '.take_report_author', report_id=REPORT_LINK_ID_PLACEHOLDER, author_form='creator')
    icon_url = url_for(LB_COVERAGE_BP_NAME + '.take_report_author', report_id=REPORT_LINK_ID_PLACEHOLDER, author_form='icon')

    set_conf('coverages_url', start + coverages_url)
    set_conf('coverage_info_url', start + coverage_info_url)
    set_conf('reports_url', start + reports_url)
    set_conf('author_url', start + author_url)
    set_conf('creator_url', start + creator_url)
    set_conf('icon_url', start + icon_url)

def update_from_cid(cid_got):
    update_ret = None

    try:
        if cid_got:
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

