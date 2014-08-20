#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json

try:
    long
except:
    long = int

from citizendesk.common.utils import get_boolean as _get_boolean

PARAGRAPH_TEXTS_SEPARATOR = '\n'

CONFIG_USE_SETUP = 'make_setup'
CONFIG_USE_REPORTS = 'public_reports'

config = {
    'field_public_report': 'assignments',
    'condition_public_report': {'$exists': True, '$not': {'$size': 0}},
}

def get_conf(name):
    global config

    if name in config:
        return config[name]
    return None

def set_conf(key, value):
    global config

    config[key] = value

def setup_config(workingon_config_data):
    if type(workingon_config_data) is not dict:
        return False
    if (CONFIG_USE_SETUP not in workingon_config_data) or (not workingon_config_data[CONFIG_USE_SETUP]):
        return False

    to_setup = _get_boolean(workingon_config_data[CONFIG_USE_SETUP])
    if not to_setup:
        return False

    if CONFIG_USE_REPORTS in workingon_config_data:
        if (workingon_config_data[CONFIG_USE_REPORTS]) and (workingon_config_data[CONFIG_USE_REPORTS] != 'assignments'):
            set_conf('field_public_report', workingon_config_data[CONFIG_USE_REPORTS])
            set_conf('condition_public_report', True)

    return True

