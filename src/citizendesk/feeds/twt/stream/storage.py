#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

USE_SEQUENCES = False

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

collection = 'twt_streams'

schema = {
    '_id': 'ObjectId',
    'spec': {
        'oauth_id': '_id of oauth info',
        'filter_id': '_id of filter info'
    },
    'control': {
        'streamer_url': 'http://localhost:9054/',
        'process_id': 'under which system id the stream runs',
        'switch_on': 'controls whether stream is active'
    },
    'logs': {
        'created': '2014-03-12T12:00:00',
        'updated': '2014-03-12T12:00:00',
        'started': '2014-03-12T12:00:00',
        'stopped': '2014-03-12T12:00:00'
    }
}

