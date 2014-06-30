#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from citizendesk.feeds.sms.citizen_alias.storage import collection, schema, AUTHORITY
from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_id, get_one_by_phone_number
from citizendesk.feeds.sms.common.utils import get_conf, citizen_holder
from citizendesk.feeds.sms.common.utils import create_identities as _create_phone_number_identities
from citizendesk.common.utils import get_id_value as _get_id_value
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
        alias_value = _get_id_value(alias_value)
        res = get_one_by_id(db, alias_value)

    if 'phone_number' == alias_type:
        try:
            phone_number = str(alias_value)
        except:
            return (False, 'wrong phone number form')
        res = get_one_by_phone_number(db, phone_number)

    if not res:
        return (False, 'unknown form of citizen alias')

    return res

def do_get_list(db, offset=None, limit=None, sort=None, other=None):
    '''
    returns data of a set of sms citizen aliases
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
            if 'user_id' not in entry['identifiers']:
                continue
            one_name['phone_number'] = entry['identifiers']['user_id']
            if not one_name['phone_number']:
                continue

            description = None
            if ('description' in entry) and entry['description']:
                description = entry['description']
            if description:
                one_name['description'] = description
            name_list = []
            for name_key in ['name_first', 'name_last', 'name_full']:
                if (name_key in entry) and entry[name_key]:
                    name_list.append(entry[name_key])
            if name_list:
                one_name['names'] = ' - '.join(name_list)

            docs.append(one_name)

    return (True, docs, {'total': total})

def do_post_one(db, alias_id, alias_spec, user_id):
    '''
    sets a basic info on phone_number-based citizen alias
    '''
    if not db:
        return (False, 'inner application error')

    if type(alias_spec) is not dict:
        return (False, 'citizen specification should be a dict')
    if 'phone_number' not in alias_spec:
        return (False, 'phone number specification not provided')
    use_phone_number = alias_spec['phone_number']
    try:
        use_phone_number = str(use_phone_number)
    except:
        return (False, 'wrong specification of phone number')
    if not use_phone_number:
        return (False, 'empty phone number specification')

    user_id = _get_id_value(user_id)

    if not alias_id:
        search_res = get_one_by_phone_number(db, use_phone_number)
        if search_res[0]:
            return (False, 'active citizen alias with given phone number already exists', search_res[1]['_id'])

    alias_doc = None
    if alias_id:
        alias_id = _get_id_value(alias_id)
        alias_doc = get_one_by_id(db, alias_id)
        if not alias_doc:
            return (False, 'citizen alias of provided id not found')

    spec_keys = {
        'description': [str, unicode],
        'name_first': [str, unicode],
        'name_last': [str, unicode],
        'name_full': [str, unicode],
        'languages': [list, tuple],
        'places': [list, tuple],
        'home_pages': [list, tuple],
        'verified': [bool]
    }

    use_identifiers = _create_phone_number_identities(use_phone_number)

    if not alias_doc:
        alias_use = {
            'authority': AUTHORITY,
            'identifiers': use_identifiers,
            'verified': False,
            'local': True,
            'created_by': user_id
        }

        for key in spec_keys:
            if (key in alias_spec) and (type(alias_spec[key]) in spec_keys[key]):
                alias_use[key] = alias_spec[key]

        alias_id = citizen_holder.save_alias(alias_use)

        if not alias_id:
            return (False, 'can not save the citizen alias')

    else:
        alias_use = alias_doc
        alias_use['identifiers'] = use_identifiers
        alias_use['updated_by'] = user_id
        alias_use['local'] = True

        for key in spec_keys:
            if (key in alias_spec) and (type(alias_spec[key]) in spec_keys[key]):
                alias_use[key] = alias_spec[key]

        coll = db[collection]
        alias_id = coll.save(alias_use)

        if not alias_id:
            return (False, 'can not update the citizen alias')

    return (True, {'_id': alias_id})

