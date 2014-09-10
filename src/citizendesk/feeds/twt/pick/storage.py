#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

collection = 'twt_picked'

schema = {
    'endpoint_id': 'ObjectId',
    'tweet_spec': {
        'tweet_id': 'str',
        'tweet_url': 'str',
    },
}
