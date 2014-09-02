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

from citizendesk.feeds.twt.oauth.storage import collection, schema, get_one, USE_SEQUENCES
from citizendesk.common.utils import get_id_value as _get_id_value

DEFAULT_LIMIT = 20

def do_get_one(db, doc_id, is_local):
    '''
    returns data of a single oauth info
    '''
    res = get_one(db, doc_id)
    if not res[0]:
        return res

    doc = res[1]
    if not is_local:
        try:
            for key in doc['spec']:
                if doc['spec'][key]:
                    doc['spec'][key] = '****' + str(doc['spec'][key])[-4:]
        except:
            pass

    return (True, doc)

def do_get_list(db, is_local, offset=None, limit=None):
    '''
    returns data of a set of oauth infos
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]
    cursor = coll.find().sort([('_id', 1)])

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
        if not is_local:
            try:
                for key in entry['spec']:
                    if entry['spec'][key]:
                        entry['spec'][key] = '****' + str(entry['spec'][key])[-4:]
            except:
                pass

        docs.append(entry)

    return (True, docs, {'total': total})

def _check_schema(spec):

    for key in schema['spec']:
        if key not in spec:
            return (False, '"spec.' + str(key) + '" is missing in the data spec')
        if spec[key] is None:
            continue
        if type(spec[key]) not in [str, unicode]:
            return (False, '"spec.' + str(key) + '" field has to be string')
    return (True,)

def do_post_one(db, doc_id=None, data=None):
    '''
    sets data of a single oauth info
    '''
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')
    spec = data['spec']

    doc_id = _get_id_value(doc_id)

    coll = db[collection]

    timepoint = datetime.datetime.utcnow()
    created = timepoint
    updated = timepoint

    if doc_id is not None:
        entry = coll.find_one({'_id': doc_id})
        if not entry:
            return (False, '"oauth" of the provided _id not found')
        try:
            if ('_created' in entry) and entry['_created']:
                created = entry['_created']
        except:
            created = timepoint

    doc = {
        '_created': created,
        '_updated': updated,
        'spec': {}
    }

    for key in schema['spec']:
        doc['spec'][key] = None
        if key in spec:
            doc['spec'][key] = spec[key]

    res = _check_schema(doc['spec'])
    if not res[0]:
        return res

    if not doc_id:
        try:
            if USE_SEQUENCES:
                entry = db['counters'].find_and_modify(query={'_id': collection}, update={'$inc': {'next':1}}, new=True, upsert=True, full_response=False)
                doc_id = entry['next']
            else:
                doc_id = ObjectId()
        except:
            return (False, 'can not create document id')

    doc['_id'] = doc_id

    doc_id = coll.save(doc)

    return (True, {'_id': doc_id})

def do_delete_one(db, doc_id):
    '''
    deletes data of a single oauth info
    '''
    if not db:
        return (False, 'inner application error')

    doc_id = _get_id_value(doc_id)

    coll = db[collection]

    coll.remove({'_id': doc_id})

    return (True, {'_id': doc_id})

