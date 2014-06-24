#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

AUTHORITY = 'twitter'

collection = 'citizen_aliases'

schema = {
    '_id': 'this is for loading citizen aliases'
}

def get_one_by_id(db, alias_id):
    '''
    returns data of a single twt citizen alias with given twt user id
    '''
    if not db:
        return (False, 'inner application error')

    try:
        alias_id = str(alias_id)
    except:
        return (False, 'wrong alias id form')

    coll = db[collection]

    spec = {'authority': AUTHORITY, 'identifiers.user_id': alias_id}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'citizen alias info not found')

    return (True, doc)

def get_one_by_name(db, alias_name):
    '''
    returns data of a single twt citizen alias with given twt user name
    '''
    if not db:
        return (False, 'inner application error')

    try:
        alias_name = str(alias_name)
    except:
        return (False, 'wrong alias name form')

    coll = db[collection]

    spec = {'authority': AUTHORITY, 'identifiers.user_name_search': alias_name.lower()}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'citizen alias info not found')

    return (True, doc)

