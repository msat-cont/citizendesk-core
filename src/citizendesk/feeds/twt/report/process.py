#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from bson.objectid import ObjectId

from citizendesk.feeds.twt.report.storage import collection, schema, FEED_TYPE, PUBLISHER_TYPE
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.common.utils import get_sort as _get_sort

DEFAULT_LIMIT = 20

'''
Here we should list (saved) reports filtered according to report_id of the requested stream.
'''

def do_get_one(db, doc_id):
    '''
    returns data of a single stream control
    '''
    if not db:
        return (False, 'inner application error')

    doc_id = _get_id_value(doc_id)
    spec_field = 'report_id'
    if type(doc_id) is ObjectId:
        spec_field = '_id'

    coll = db[collection]
    doc = coll.find_one({'feed_type': FEED_TYPE, spec_field: doc_id})

    if not doc:
        return (False, 'report not found')

    return (True, doc)

def do_get_list(db, endpoint_type, endpoint_id, proto=None, offset=None, limit=None, sort=None, other=None):
    '''
    returns data of a set of reports saved by a stream or a search
    '''
    if not db:
        return (False, 'inner application error')

    endpoint_id = _get_id_value(endpoint_id)

    list_spec = {'feed_type': FEED_TYPE, 'channels': {'$elemMatch': {'type': endpoint_type, 'value': endpoint_id}}}
    if proto is not None:
        try:
            proto = bool(_get_boolean(proto))
        except:
            return (False, 'the "proto" specifier has to be a boolean value')
        list_spec['proto'] = proto

    sort_list = _get_sort(sort)
    if not sort_list:
        sort_list = [('produced', 1)]

    text_only = False
    if other and ('text_only' in other) and other['text_only']:
        try:
            text_only = bool(_get_boolean(other['text_only']))
        except:
            text_only = False

    coll = db[collection]
    cursor = coll.find(list_spec).sort(sort_list)

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
        if not text_only:
            docs.append(entry)
        else:
            if (not 'texts' in entry):
                continue
            if (not entry['texts']):
                continue
            if (type(entry['texts']) not in [list]):
                continue
            for one_text in entry['texts']:
                source = None
                if ('sources' in entry) and (type(entry['sources']) is list):
                    if len(entry['sources']) and (entry['sources'][0]):
                        source = entry['sources'][0]
                if source:
                    if (type(one_text) is dict):
                        one_text['source'] = source
                docs.append(one_text)

    return (True, docs, {'total': total})

def do_get_session(db, session, offset=None, limit=None):
    '''
    returns data of a set of reports saved by the stream
    '''
    if not db:
        return (False, 'inner application error')

    session = _get_id_value(session)

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
        doc_id = _get_id_value(doc_id)

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

    spec_field = 'report_id'
    if type(doc_id) is ObjectId:
        spec_field = '_id'

    coll.update({'feed_type': FEED_TYPE, spec_field: doc_id}, {'$set': {'proto': proto}}, upsert=False)

    return (True, {'report_id': doc_id})

