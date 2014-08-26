#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

FIELD_UPDATED = '_updated'
FIELD_DECAYED = 'decayed'
FIELD_UUID = 'uuid'
FIELD_PUTUP = 'status_updated'
FIELD_PUTUP = '_updated' # this is temporary hack until we have set the proper field in UI; remove this line then.
FIELD_MEDIA = 'media'
MEDIA_IMAGE_TYPE = 'image'

FIELD_ASSIGNED = 'assignments'
FIELD_STATUS = 'status'

collection = 'reports'

schema = {
    '_id': 'this is for loading the whole reports'
}

def get_report_by_id(db, report_id):
    '''
    returns data of a single report
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'_id': report_id}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'report not found')

    return (True, doc)

def update_report_set(db, report_id, update_set):
    '''
    updates data of a single report
    '''
    if not db:
        return (False, 'inner application error')

    check = get_report_by_id(db, report_id)
    if not check[0]:
        return (False, 'no such report')

    coll = db[collection]

    try:
        coll.update({'_id': report_id}, {'$set': update_set})
    except:
        return (False, 'can not make report update')

    return (True, {'_id': report_id})

