#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, random
try:
    import yaml
except:
    #logging.error('Can not load YAML support')
    sys.exit(1)
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger
from citizendesk.common.holder import ReportHolder
from citizendesk.common.citizen_holder import CitizenHolder
from citizendesk.ingest.url.eff_tlds import take_tlds_sets

report_holder = ReportHolder()
citizen_holder = CitizenHolder()

COLL_CONFIG = 'core_config'

config = {
    'feed_type': 'web_link',
    'authority': 'web',
    'eff_tlds': None,
}

def set_conf(key, value):
    global config

    config[key] = value

def get_conf(key):
    global config

    if key not in config:
        return None

    return config[key]

def set_effective_tlds(file_path):
    tld_sets = take_tlds_sets(file_path)

    set_conf('eff_tlds', tld_sets)

