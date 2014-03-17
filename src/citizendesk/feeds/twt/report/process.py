#!/usr/bin/env python
#
# Citizen Desk
#

FEED_TYPE = 'tweet'
CHANNEL_TYPE = 'twitter'

collection = 'reports'

schema = {
    '_id': 'this is for loading the whole reports'
}

'''
Here we should list (saved) reports filtered according to _id of the requested stream.
'''

def do_get_one(db, doc_id):
    '''
    returns data of a single stream control
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]
    doc = coll.find_one({'_id': doc_id})

    return (True, doc)

def do_get_list(db, stream_id, proto, offset=0, limit=20):
    '''
    returns data of a set of reports saved by the stream
    '''
    if not holder:
        return (False, 'inner application error')

    coll = db[collection]
    cursor = coll.find({'feed_type': FEED_TYPE, 'channels': {'$elemMatch': {'type': CHANNEL_TYPE, 'value': stream_id}}})

    if offset:
        cursor = cursor.skip(offset)
    if limit:
        cursor = cursor.limit(limit)

    docs = []
    for entry in cursor:
        if not entry:
            continue
        docs.append(entry)

    return (True, docs)

def do_post_one_proto(db, doc_id, proto):
    pass


