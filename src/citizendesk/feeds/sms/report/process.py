#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from citizendesk.feeds.sms.report.storage import collection, schema, FEED_TYPE, PUBLISHER_TYPE
from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_sort as _get_sort

DEFAULT_LIMIT = 20

'''
Here we should list (saved) reports filtered according to _id of saved sms-based reports.
'''

def do_get_one(db, doc_id):
    '''
    returns data of a single citizen alias
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    doc_id = _get_id_value(doc_id)

    spec = {'_id': doc_id, 'feed_type': FEED_TYPE}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'report not found')

    return (True, doc)

def do_get_list(db, spec_type, spec_id, offset=None, limit=None, sort=None, other=None):
    '''
    returns data of a set of sms citizen aliases
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {'feed_type': FEED_TYPE}
    if 'session_id' == spec_type:
        list_spec['session'] = spec_id
    if 'sent_to' == spec_type:
        list_spec['recipients.identifiers'] = {'type':'phone_number', 'value':spec_id}
    if 'received_from' == spec_type:
        list_spec['authors.identifiers'] = {'type':'phone_number', 'value':spec_id}

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
            one_name = {
                'original': None,
                'authors': None,
                'recipients': None,
            }
            if 'original' in entry:
                one_name['original'] = entry['original']
            if 'authors' in entry:
                one_name['authors'] = entry['authors']
            if 'recipients' in entry:
                one_name['recipients'] = entry['recipients']
            if (not one_name['original']) and (not one_name['authors']) and (not one_name['recipients']):
                continue
            docs.append(one_name)

    return (True, docs, {'total': total})
