#!/usr/bin/env python
#
# Citizen Desk
#
'''
'''

import os, sys, datetime, json
from bson import json_util
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips
from citizendesk.common.dbc import mongo_dbs

bp_feed_sms_report = Blueprint('bp_feed_sms_report', __name__)

def setup_blueprints(app):
    app.register_blueprint(bp_feed_sms_report)
    return



