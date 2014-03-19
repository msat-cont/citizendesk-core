#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from citizendesk.feeds.twt.report.storage import collection, schema, FEED_TYPE, CHANNEL_TYPE

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

    if not doc:
        return (False, 'report not found')

    return (True, doc)

def _get_boolean(value):
    if not value:
        return False
    if type(value) is bool:
        return value

    if value in [0, '0']:
        return False
    if value in [1, '1']:
        return True

    if type(value) in [str, unicode]:
        if value.startswith('t'):
            return True
        if value.startswith('T'):
            return True
        if value.startswith('f'):
            return False
        if value.startswith('F'):
            return False

    return None

def do_get_list(db, stream_id, proto=None, offset=0, limit=20):
    '''
    returns data of a set of reports saved by the stream
    '''
    if not db:
        return (False, 'inner application error')

    try:
        proto = bool(_get_boolean(proto))
    except:
        proto = None

    list_spec = {'feed_type': FEED_TYPE, 'channels': {'$elemMatch': {'type': CHANNEL_TYPE, 'value': stream_id}}}
    if proto is not None:
        list_spec['proto'] = proto

    coll = db[collection]
    cursor = coll.find(list_spec).sort([('produced', 1)])

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

def do_get_session(db, session, offset=0, limit=20):
    '''
    returns data of a set of reports saved by the stream
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {'feed_type': FEED_TYPE, 'session': session}

    coll = db[collection]
    cursor = coll.find(list_spec).sort([('produced', 1)])

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

def do_patch_one(db, doc_id=None, data=None):
    '''
    sets the "proto" field value
    '''
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if type(data) is not dict:
        return (False, 'data should be a dict')
    if 'proto' not in data:
        return (False, 'data should contain a "proto" field')

    try:
        proto = bool(_get_boolean(data['proto']))
    except:
        return (False, 'the "proto" parameter has to be boolean value')

    res = do_get_one(db, doc_id)
    if not res[0]:
        return res

    coll = db[collection]

    coll.update({'_id': doc_id}, {'$set': {'proto': proto}}, upsert=False)

