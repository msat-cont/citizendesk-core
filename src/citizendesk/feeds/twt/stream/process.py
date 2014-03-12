#!/usr/bin/env python
#
# Citizen Desk
#

collection = 'twt_streams'

schema = {
    'oauth_id': '_id of oauth spec',
    'filter_id': '_id of filter spec',
    'endpoint_id': 'to which endpoint is this stream connected',
    'status': 'controls whether stream is active'
}

'''
For this case, we have to check the status(es) on each GET request.
And for POST requests, we have to stop the stream if it is active and anything changes.
Notice that a single oauth spec can be only used on a single stream.
'''

def do_get_one(holder, doc_id):
    '''
    returns data of a single stream control
    '''
    if not holder:
        return (False, 'inner application error')

    coll = holder.get_collection[collection]
    doc = coll.find_one({'_id': doc_id})

    return (True, doc)

def do_get_list(holder, offset=0, limit=20):
    '''
    returns data of a set of stream control
    '''
    if not holder:
        return (False, 'inner application error')

    coll = holder.get_collection[collection]
    cursor = coll.find()
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

def do_post_one(holder, doc_id=None, data=None):
    '''
    sets -- or deletes if data is None -- data of a single stream control
    '''
    if not holder:
        return (False, 'inner application error')

    if (doc_id is None) and (data is None):
        return (False, 'neither doc_id nor data is provided')

    coll = holder.get_collection[collection]

    if data is None:
        coll.remove({'_id': doc_id})
    else:
        doc = {}
        if doc_id:
            doc['_id'] = doc_id
        for key in schema:
            doc[key] = None
            if key in data:
                doc[key] = data[key]

        doc_id = coll.save(doc)

    return (True, doc_id)


