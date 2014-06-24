#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from citizendesk.feeds.sms.common.utils import get_conf

AUTHORITY = 'telco'

collection = 'citizen_aliases'

schema = {
    '_id': 'when updating an existent citizen alias',
    'user_id': 'who created or updated this citizen alias',
    'spec': {
        'phone_number': '+1234567890; required',
        'description': 'info on the citizen alias',
        'name_first': 'John',
        'name_last': 'Dow',
        'name_full': 'when name_first and name_full are not suitable',
        'languages': ['en', 'es'],
        'places': ['Maputo', 'Mozambique'],
        'home_pages': ['http://www.sourcefabric.org/'],
        'verified': False
    }
}

def get_one_by_id(db, alias_id):
    '''
    returns data of a single sms citizen alias with given sms alias id
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'_id': alias_id, 'authority': AUTHORITY}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'citizen alias info not found')

    return (True, doc)

def get_one_by_phone_number(db, phone_number, active=True):
    '''
    returns data of a single sms citizen alias with given phone number
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'active': active, 'authority': AUTHORITY, 'identifiers.user_id': phone_number}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'citizen alias info not found')

    return (True, doc)

