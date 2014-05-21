#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

from citizendesk.feeds.twt.filter.storage import collection, schema, get_one

DEFAULT_LIMIT = 20

def do_get_one(db, doc_id):
    '''
    returns data of a single filter info
    '''
    return get_one(db, doc_id)

def do_get_list(db, offset=None, limit=None):
    '''
    returns data of a set of filter infos
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
        docs.append(entry)

    return (True, docs, {'total': total})

def _check_schema(spec):
        some_data = False

        if ('follow' in spec) and spec['follow']:
            if type(spec['follow']) not in (list, tuple):
                return (False, '"spec.follow" field has to be list')
            for value in spec['follow']:
                some_data = True
                if type(value) not in [str, unicode]:
                    return (False, '"spec.follow" field has to be list of strings')
        if ('track' in spec) and spec['track']:
            if type(spec['track']) not in (list, tuple):
                return (False, '"spec.track" field has to be list')
            for value in spec['track']:
                some_data = True
                if type(value) not in [str, unicode]:
                    return (False, '"spec.track" field has to be list of strings')
                if ',' in value:
                    return (False, '"spec.track" field values can not contain comma "," since it is used as a value separator')
        if ('locations' in spec) and spec['locations']:
            if type(spec['locations']) not in (list, tuple):
                return (False, '"spec.locations" field has to be list')
            for value in spec['locations']:
                some_data = True
                if type(value) not in [dict]:
                    return (False, '"spec.locations" field has to be list of dicts')
                location_keys = ['west', 'east', 'north', 'south']
                for key in location_keys:
                    if not key in value:
                        return (False, '"spec.locations" field value lacks ' + str(key) + ' key')
                for key in value:
                    if key not in location_keys:
                        return (False, '"spec.locations" field value keys have to be "west", "east", "south", "north"')
                    if type(value[key]) not in [int, long, float]:
                        return (False, '"spec.locations" field values have to be numbers')
        if ('language' in spec) and spec['language']:
            if type(spec['language']) not in [str, unicode]:
                return (False, '"spec.language" field has to be string')

        if not some_data:
            return (False, 'empty filter')

        return (True,)

def do_post_one(db, doc_id=None, data=None):
    '''
    sets data of a single filter info
    '''
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')
    spec = data['spec']

    if doc_id is not None:
        if doc_id.isdigit():
            try:
                doc_id = int(doc_id)
            except:
                pass

    coll = db[collection]

    timepoint = datetime.datetime.utcnow()
    created = timepoint
    updated = timepoint

    if doc_id is not None:
        entry = coll.find_one({'_id': doc_id})
        if not entry:
            return (False, '"filter" of the provided _id not found')
        try:
            if ('logs' in entry) and (entry['logs']) and ('created' in entry['logs']):
                if entry['logs']['created']:
                    created = entry['logs']['created']
        except:
            created = timepoint

    doc = {
        'logs': {
            'created': created,
            'updated': updated
        },
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
            entry = db['counters'].find_and_modify(query={'_id': collection}, update={'$inc': {'next':1}}, new=True, upsert=True, full_response=False);
            doc_id = entry['next']
        except:
            return (False, 'can not create document id')

    doc['_id'] = doc_id

    doc_id = coll.save(doc)

    return (True, {'_id': doc_id})

def do_delete_one(db, doc_id):
    '''
    deletes data of a single filter info
    '''
    if not db:
        return (False, 'inner application error')

    if doc_id is not None:
        if doc_id.isdigit():
            try:
                doc_id = int(doc_id)
            except:
                pass

    coll = db[collection]

    coll.remove({'_id': doc_id})

    return (True, {'_id': doc_id})

