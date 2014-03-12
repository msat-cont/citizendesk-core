#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

collection = 'twt_filters'

schema = {
    '_id': 1,
    'spec': {
        'follow': ['6253282'],
        'track': ['citizen desk', 'citizendesk'],
        'locations': [{'west': -74, 'east': -73, 'south': 40, 'north': 41}],
        'language': 'en'
    },
    'logs': {
        'created': '2014-03-12T12:00:00',
        'updated': '2014-03-12T12:10:00'
    }
}

def do_get_one(db, doc_id):
    '''
    returns data of a single filter spec
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
    doc = coll.find_one({'_id': doc_id})

    return (True, doc)

def do_get_list(db, offset=0, limit=20):
    '''
    returns data of a set of filter specs
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]
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

def _check_schema(doc):

        if doc['follow']:
            if type(doc['follow']) is not list:
                return (False, '"follow" field has to be list')
            for value in doc['follow']:
                if type(value) not in [str, unicode]:
                    return (False, '"follow" field has to be list of strings')
                if not value.isdigit():
                    return (False, '"follow" field values have to be digiatl strings')
        if doc['track']:
            if type(doc['track']) is not list:
                return (False, '"track" field has to be list')
            for value in doc['track']:
                if type(value) not in [str, unicode]:
                    return (False, '"track" field has to be list of strings')
                if ',' in value:
                    return (False, '"track" field values can not contain comma "," since it is used as a value separator')
        if doc['locations']:
            if type(doc['locations']) is not list:
                return (False, '"locations" field has to be list')
            for value in doc['locations']:
                if type(value) not in [dict]:
                    return (False, '"locations" field has to be list of dicts')
                location_keys = ['west', 'east', 'north', 'south']
                for key in location_keys:
                    if not key in value:
                        return (False, '"locations" field value lacks ' + str(key) + ' key')
                for key in value:
                    if key not in location_keys:
                        return (False, '"locations" field values only have to have "west", "east", "south", "north" keys')
                    if type(value[key]) is not int:
                        return (False, '"locations" field value keys have to be integers')
        if doc['language']:
            if type(doc['language']) not in [str, unicode]:
                return (False, '"language" field has to be string')

        return (True,)

def do_post_one(db, doc_id=None, data=None):
    '''
    sets data of a single filter spec
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
    deletes data of a single filter spec
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    coll.remove({'_id': doc_id})

    return (True, {'_id': doc_id})

