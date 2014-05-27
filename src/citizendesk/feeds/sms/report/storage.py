#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

FEED_TYPE = 'sms'
PUBLISHER_TYPE = 'sms_gateway'

collection = 'reports'

schema = {
    '_id': 'this is for loading the whole reports'
}

