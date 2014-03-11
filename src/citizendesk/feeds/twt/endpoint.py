#!/usr/bin/env python
#
# Citizen Desk
#

collection = 'reports'

schema = {
    '_': 'virtual collection for listing reports saved (in a stream) by a provided endpoint_id'
}

'''
Here we should list (saved) reports filtered according to the endpoint's _id.
'''

def do_get_list(holder, endpoint_id, offset=0, limit=20):
    '''
    returns data of a set of reports saved by the endpoint
    '''
    if not holder:
        return (False, 'inner application error')

    coll = holder.get_collection[collection]
    cursor = coll.find({'feed_type': tweet, 'channels': {'$elemMatch': {'type': twitter, 'value': endpoint_id}}})

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

