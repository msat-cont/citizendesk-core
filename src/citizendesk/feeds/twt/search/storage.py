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

collection = 'twt_searches'

schema = {
    'user_id': 1,
    'request_id': 1000,
    'search_spec': {
        'query': {
            'having_any': False,
            'contains': ['keyword', '#hashtag', '@mentioned_name'],
            'from': 'sender_name',
            'to': 'recipient_name',
            'without': 'avoid_word',
            'since': '2012-01-01',
            'until': '2014-12-31'
        },
        'geo': {'latitude': '50.0889', 'longitude': '14.4213', 'radius': '1', 'radius_unit': 'km'},
        'lang': 'en',
        'count': 30,
        'since_id': '454174577846140928',
        'max_id': '458630141250666496',
        'result_type': 'mixed'
    }
}

