#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

FEED_TYPE = 'tweet'
PUBLISHER_TYPE = 'twitter'

collection = 'reports'

schema = {
    '_id': 'this is for loading the whole reports'
}

