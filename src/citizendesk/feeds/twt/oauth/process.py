#!/usr/bin/env python
#
# Citizen Desk
#

collection = 'twt_oauths'

schema = {
    'consumer_key': 'YOUR TWITER Consumer key',
    'consumer_secret': 'YOUR TWITER Consumer secret',
    'access_token_key': 'YOUR TWITER Access token',
    'access_token_secret': 'YOUR TWITER Access token secret'
}

def do_get_one(holder, doc_id):
    '''
    returns data of a single oauth spec
    '''
    if not holder:
        return (False, 'inner application error')

    coll = holder.get_collection[collection]
    doc = coll.find_one({'_id': doc_id})

    return (True, doc)

def do_get_list(holder, offset=0, limit=20):
    '''
    returns data of a set of oauth specs
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
    sets -- or deletes if data is None -- data of a single oauth spec
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


