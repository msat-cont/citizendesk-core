#!/usr/bin/env python
#
# Citizen Desk
#

PUBLISHED_REPORTS_PLACEHOLDER = '__coverage_id_placeholder__'
CITIZEN_PLACEHOLDER = '__citizen_id_placeholder__'

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

