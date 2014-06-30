#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

FEED_TYPE = 'sms'
PUBLISHER_TYPE = 'sms_gateway'

collection = 'reports'

schema = {
    '_id': 'this is for loading the whole reports'
}

def do_get_one_by_id(db, doc_id):
    '''
    returns data of a single citizen alias
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'_id': doc_id, 'feed_type': FEED_TYPE}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'report not found')

    return (True, doc)

