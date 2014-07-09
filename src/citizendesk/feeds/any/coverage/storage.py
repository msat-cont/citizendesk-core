#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

FIELD_ACTIVE = 'is_active'
FIELD_DECAYED = 'is_decayed'

collection = 'coverages'

schema = {
    '_id': 'ObjectId',
    'title': 'str',
    'description': 'str',
    'user_id': 'ObjectId',
    'is_active': 'bool',
    'is_decayed': 'bool',
}

def get_coverage_by_id(db, coverage_id):
    '''
    returns data of a single coverage
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'_id': doc_id}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'coverage not found')

    return (True, doc)

def update_coverage_set(db, coverage_id, update_set):
    '''
    updates data of a single coverage_id
    '''
    if not db:
        return (False, 'inner application error')

    check = get_coverage_id_by_id(db, coverage_id)
    if not check[0]:
        return (False, 'no such coverage')

    coll = db[collection]

    try:
        coll.update({'_id': coverage_id}, {'$set': update_set})
    except:
        return (False, 'can not make coverage update')

    return (True, {'_id': coverage_id})

