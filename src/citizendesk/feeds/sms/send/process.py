#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
try:
    from citizendesk.feeds.twt.external import newstwister as controller
except:
    controller = None

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

from citizendesk.feeds.sms.send.storage import collection, schema
from citizendesk.common.utils import get_boolean as _get_boolean

'''
'''

def do_post_search(db, sms_gateway_url, message, recipients):
    pass



