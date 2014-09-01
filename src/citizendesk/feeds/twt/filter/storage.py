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

collection = 'twt_filters'

schema = {
    '_id': 1,
    'spec': {
        'follow': ['sourcefabric'], # notice that this shall be translated into ids before sending to Newstwister, e.g. 121151264,
        'track': ['citizen desk', '#citizendesk', '@sourcefabric'],
        'locations': [{'name': 'New York', 'west': -74, 'east': -73, 'south': 40, 'north': 41}],
        'language': 'en'
    },
    '_created': 'datetime',
    '_updated': 'datetime',
}

def get_one(db, doc_id):
    '''
    returns data of a single filter info
    '''
    if not db:
        return (False, 'inner application error')

    doc_id = _get_id_value(doc_id)

    coll = db[collection]
    doc = coll.find_one({'_id': doc_id})

    if not doc:
        return (False, 'filter info not found')

    return (True, doc)

