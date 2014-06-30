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

# this is for loading the whole reports
schema = {
    '_id': 'ObjectID',
    'report_id': 'feed type-related string id',
    'parent_id': 'for linking among reports even when they are not stored (yet)',
    'session_id': 'grouping based on feed type-related ids',
}

