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

collection = 'twt_oauths'

schema = {
    '_id': 'ObjectId',
    'spec': {
        'consumer_key': 'YOUR TWITER Consumer key',
        'consumer_secret': 'YOUR TWITER Consumer secret',
        'access_token_key': 'YOUR TWITER Access token',
        'access_token_secret': 'YOUR TWITER Access token secret'
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
