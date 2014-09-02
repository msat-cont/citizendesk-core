#!/usr/bin/env python
#
# Citizen Desk
#

LB_COVERAGE_BP_NAME = 'bp_outgest_lb_coverage_take'

COVERAGE_PLACEHOLDER = '__coverage_id_placeholder__'
PUBLISHED_REPORTS_PLACEHOLDER = '__coverage_id_placeholder__'
REPORT_LINK_ID_PLACEHOLDER = '__report_link_id_placeholder__'

STATUS_PHRASING_FIELD = 'description'
STATUS_KEY_FIELD = 'key'

STATUS_PHRASING_CONFIG_TEMPLATE = 'status_phrase_<<status>>_report'
STATUS_PHRASING_CONFIG_REPLACE = '<<status>>'

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

COLL_CONFIG = 'core_config'
COLL_REPORT_STATUS = 'report_statuses'

config_default = {
}
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

def set_conf_default(key, value):
    global config_default

    config_default[key] = value

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
        'use_status_for_output',
        'status_display_position',
        'status_phrase_new_report',
        'status_phrase_assigned_report',
        'status_phrase_dismissed_report',
        'status_phrase_false_report',
        'status_phrase_verified_report',
    ]

    for one_key in use_keys:
        if (one_key in liveblog_config_data) and liveblog_config_data[one_key]:
            set_conf(one_key, liveblog_config_data[one_key])
            set_conf_default(one_key, liveblog_config_data[one_key])

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

def use_liveblog_configuration(db):
    global config
    global config_default

    lb_config = {}
    for key in config_default:
        lb_config[key] = config_default[key]

    lb_config_db = {}
    found_config = db[COLL_CONFIG].find_one({'type': 'liveblog'})
    if found_config and (type(found_config) is dict):
        if ('set' in found_config) and (type(found_config['set']) is dict):
            lb_config_db = found_config['set']

    for key in lb_config:
        if (key in lb_config_db) and (lb_config_db[key] is not None):
            lb_config[key] = lb_config_db[key]

    for key in lb_config:
        set_conf(key, lb_config[key])

def take_status_desc_by_id(db, status_id):
    phrasing = None

    found_status = db[COLL_REPORT_STATUS].find_one({'_id': status_id})
    if found_status:
        if (type(found_status) is dict) and (STATUS_PHRASING_FIELD in found_status):
            if found_status[STATUS_PHRASING_FIELD] is not None:
                phrasing = found_status[STATUS_PHRASING_FIELD]

    return phrasing

def take_status_desc_by_key(db, status_key):
    phrasing = None

    try:
        phrasing = get_conf(STATUS_PHRASING_CONFIG_TEMPLATE.replace(STATUS_PHRASING_CONFIG_REPLACE, status_key))
    except:
        phrasing = None

    found_status = db[COLL_REPORT_STATUS].find_one({STATUS_KEY_FIELD: status_key})
    if found_status:
        if (type(found_status) is dict) and (STATUS_PHRASING_FIELD in found_status):
            if found_status[STATUS_PHRASING_FIELD] is not None:
                phrasing = found_status[STATUS_PHRASING_FIELD]

    return phrasing

