#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from citizendesk.common.utils import get_etag as _get_etag

FIELD_ACTIVE = 'active'
FIELD_DECAYED = 'decayed'

collection = 'coverages'

schema = {
    '_id': 'ObjectId',
    'title': 'str',
    'description': 'str',
    'uuid': 'uuid4',
    'user_id': 'ObjectId',
    FIELD_ACTIVE: 'bool',
    FIELD_DECAYED: 'bool',
}

def get_coverage_by_id(db, coverage_id):
    '''
    returns data of a single coverage
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'_id': coverage_id}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'coverage not found')

    return (True, doc)

def get_coverage_by_uuid(db, coverage_uuid):
    '''
    returns data of a single coverage
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'uuid': coverage_uuid}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'coverage not found')

    return (True, doc)

def update_coverage_set(db, coverage_sel, update_set):
    '''
    updates data of a single coverage_id
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    doc = coll.find_one(coverage_sel)
    if not doc:
        return (False, 'no such coverage')

    try:
        #update_set['_etag'] = _get_etag()

        coll.update(coverage_sel, {'$set': update_set})
    except:
        return (False, 'can not make coverage update')

    return (True, {'_id': coverage_id})

