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

collection = 'twt_filters'

schema = {
    '_id': 1,
    'spec': {
        'follow': ['sourcefabric'], # notice that this shall be translated into ids before sending to Newstwister, e.g. 121151264,
        'track': ['citizen desk', '#citizendesk', '@sourcefabric'],
        'locations': [{'name': 'New York', 'west': -74, 'east': -73, 'south': 40, 'north': 41}],
        'language': 'en'
    },
    'logs': {
        'created': '2014-03-12T12:00:00',
        'updated': '2014-03-12T12:10:00'
    }
}

def get_one(db, doc_id):
    '''
    returns data of a single filter info
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
        return (False, 'filter info not found')

    return (True, doc)

