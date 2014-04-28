#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
from bson.objectid import ObjectId

try:
    unicode
except:
    unicode = str

collection = 'twt_oauths'

schema = {
    '_id': 1,
    'spec': {
        'consumer_key': 'YOUR TWITER Consumer key',
        'consumer_secret': 'YOUR TWITER Consumer secret',
        'access_token_key': 'YOUR TWITER Access token',
        'access_token_secret': 'YOUR TWITER Access token secret'
    },
    'logs': {
        'created': '2014-03-12T12:00:00',
        'updated': '2014-03-12T12:00:00'
    }
}

def get_one(db, doc_id):
    '''
    returns data of a single oauth info
    '''
    if not db:
        return (False, 'inner application error')

    try:
        doc_id = ObjectId(doc_id)
    except:
        pass

    if type(doc_id) in [str, unicode]:
        if doc_id.isdigit():
            try:
                doc_id = int(doc_id)
            except:
                pass

    coll = db[collection]
    doc = coll.find_one({'_id': doc_id})

    if not doc:
        return (False, 'oauth info not found')

    return (True, doc)
