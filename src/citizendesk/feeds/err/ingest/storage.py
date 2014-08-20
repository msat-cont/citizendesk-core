#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

collection = 'ingest_notices'

schema = {
    '_id': 'ObjectId',
    '_created': 'timestamp',
    '_updated': 'timestamp',
    'produced': 'timestamp',
    'feed_type': 'str',
    'channel': 'dict',
    'message': 'str',
}

