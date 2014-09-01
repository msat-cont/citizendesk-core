#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
from bson.objectid import ObjectId

from citizendesk.common.utils import get_id_value as _get_id_value

USE_SEQUENCES = False

try:
    unicode
except:
    unicode = str

collection = 'twt_authorized'

schema = {
    '_id': 'ObjectId',
    'spec': {
        'app_consumer_key': 'Application Consumer key',
        'app_consumer_secret': 'Application Consumer secret',
        'temporary_access_token_key': 'Temporary Access token',
        'temporary_access_token_secret': 'Temporary Access token secret',
        'authorized_access_token_key': 'Authorized Access token',
        'authorized_access_token_secret': 'Authorized Access token secret',
        'verifier_url': 'URL where a Twitter user cam authorize the app',
        'user_id': 'Twitter user id that authorized the app',
        'screen_name': 'Twitter user screen name that authorized the app',
        'screen_name_search': 'Lower-case version of Twitter user screen name that authorized the app',
    },
    '_created': 'datetime',
    '_updated': 'datetime',
}

def get_one(db, doc_id):
    '''
    returns data of a single oauth info
    '''
    if not db:
        return (False, 'inner application error')

    doc_id = _get_id_value(doc_id)

    coll = db[collection]
    doc = coll.find_one({'_id': doc_id})

    if not doc:
        return (False, 'oauth info not found')

    return (True, doc)
