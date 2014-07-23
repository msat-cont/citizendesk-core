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

collection = 'twt_tweets'

schema = {
    'user_id': 'ObjectId',
    'endpoint_id': 'ObjectId',
    'tweet_spec': {
        'message': 'tweet text',
        'sensitive': 'bool',
        'lat': 'str',
        'long': 'str',
        'place_id': 'str',
        'display_coordinates': 'bool',
    },
}
