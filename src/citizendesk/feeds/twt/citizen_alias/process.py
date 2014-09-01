#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
try:
    from citizendesk.feeds.twt.external import newstwister as controller
except:
    controller = None

try:
    unicode
except:
    unicode = str

from citizendesk.feeds.twt.citizen_alias.storage import collection, schema, AUTHORITY
from citizendesk.feeds.twt.citizen_alias.storage import get_one_by_id, get_one_by_name
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_sort as _get_sort

DEFAULT_LIMIT = 20

'''
Here we should list (saved) or request (if not saved) citizen aliases
'''

def do_get_one(db, alias_type, alias_value):
    '''
    returns data of a single citizen alias
    '''
    if not db:
        return (False, 'inner application error')

    res = None

    if 'alias_id' == alias_type:
        res = get_one_by_id(db, alias_value)
    if 'alias_name' == alias_type:
        res = get_one_by_name(db, alias_value)
    if not res:
        return (False, 'unknown form of citizen alias')

    return res

def do_get_list(db, offset=None, limit=None, sort=None, other=None):
    '''
    returns data of a set of twt citizen aliases
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {'authority': AUTHORITY}
    sort_list = _get_sort(sort)
    if not sort_list:
        sort_list = [('produced', 1)]

    name_only = False
    if other and ('name_only' in other) and other['name_only']:
        try:
            name_only = bool(_get_boolean(other['name_only']))
        except:
            name_only = False

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
        if not name_only:
            docs.append(entry)
        else:
            if (not 'identifiers' in entry):
                continue
            if type(entry['identifiers']) is not dict:
                continue
            one_name = {}
            if 'user_id' in entry['identifiers']:
                one_name['user_id'] = entry['identifiers']['user_id']
            if 'user_name' in entry['identifiers']:
                one_name['user_name'] = entry['identifiers']['user_name']

            source = None
            if ('sources' in entry) and (type(entry['sources']) in (list, tuple)):
                if len(entry['sources']) and (entry['sources'][0]):
                    source = entry['sources'][0]
            if source:
                one_name['source'] = source
            docs.append(one_name)

    return (True, docs, {'total': total})

def do_request_one(db, searcher_url, alias_type, alias_value):
    '''
    asks Newstwister for info on a given twt user
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if not alias_value:
        return (False, 'empty provided citizen alias')

    request_type = None

    if 'alias_id' == alias_type:
        request_type = 'user_id'
    if 'alias_name' == alias_type:
        request_type = 'user_name'
    if not request_type:
        return (False, 'unknown form of requested citizen alias')

    search_spec = {}
    search_spec[request_type] = alias_value

    connector = controller.NewstwisterConnector(searcher_url)
    res = connector.request_user(search_spec)

    if not res[0]:
        return (False, 'error during user-search request dispatching', str(res[1]))

    return (True, res[1])

