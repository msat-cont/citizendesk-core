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
from citizendesk.common.utils import get_boolean as _get_boolean

DEFAULT_LIMIT = 20

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

def do_get_list(db, stream_id, proto=None, offset=None, limit=None):
    '''
    returns data of a set of reports saved by the stream
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {'feed_type': FEED_TYPE, 'channels': {'$elemMatch': {'type': CHANNEL_TYPE, 'value': stream_id}}}
    if proto is not None:
        try:
            proto = bool(_get_boolean(proto))
        except:
            return (False, 'the "proto" specifier has to be a boolean value')
        list_spec['proto'] = proto

    coll = db[collection]
    cursor = coll.find(list_spec).sort([('produced', 1)])

    total = cursor.count()

    if limit is None:
        limit = DEFAULT_LIMIT

    if offset:
        cursor = cursor.skip(offset)
    if limit:
        cursor = cursor.limit(limit)

    docs = []
    for entry in cursor:
        if not entry:
            continue
        docs.append(entry)

    return (True, docs, {'total': total})

def do_get_session(db, session, offset=None, limit=None):
    '''
    returns data of a set of reports saved by the stream
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {'feed_type': FEED_TYPE, 'session': session}

    coll = db[collection]
    cursor = coll.find(list_spec).sort([('produced', 1)])

    total = cursor.count()

    if limit is None:
        limit = DEFAULT_LIMIT

    if offset:
        cursor = cursor.skip(offset)
    if limit:
        cursor = cursor.limit(limit)

    docs = []
    for entry in cursor:
        if not entry:
            continue
        docs.append(entry)

    return (True, docs, {'total': total})

def do_patch_one(db, doc_id=None, data=None):
    '''
    sets the "proto" field value
    '''
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if doc_id is not None:
        if doc_id.isdigit():
            try:
                doc_id = int(doc_id)
            except:
                pass

    if type(data) is not dict:
        return (False, 'data should be a dict')
    if ('proto' not in data) or (data['proto'] is None):
        return (False, 'data should contain a "proto" field')

    try:
        proto = bool(_get_boolean(data['proto']))
    except:
        return (False, 'the "proto" field has to be a boolean value')

    res = do_get_one(db, doc_id)
    if not res[0]:
        return res

    coll = db[collection]

    coll.update({'_id': doc_id}, {'$set': {'proto': proto}}, upsert=False)
