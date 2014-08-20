#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from bson.objectid import ObjectId

from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_sort as _get_sort
from citizendesk.feeds.err.ingest.storage import collection, schema

DEFAULT_LIMIT = 20

def do_get_list(db, offset, limit, sort, other):
    '''
    returns list of notices
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {}

    sort_list = _get_sort(sort)
    if not sort_list:
        sort_list = [('produced', 1)]

    text_only = False
    if other and ('text_only' in other) and other['text_only']:
        try:
            name_only = bool(_get_boolean(other['text_only']))
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
        if not text_only:
            docs.append(entry)
        else:
            if 'message' not in entry:
                continue

            one_text = {
                'message': entry['message'],
            }

            docs.append(one_text)

    return (True, docs, {'total': total})

def do_insert_one(db, notice_timestamp, notice_data):
    '''
    saves a notice
    '''
    if not db:
        return (False, 'inner application error')

    timestamp = datetime.datetime.now()

    try:
        produced_timestamp = datetime.datetime.strptime(notice_timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    except:
        try:
            produced_timestamp = datetime.datetime.strptime(notice_timestamp, '%Y-%m-%dT%H:%M:%S')
        except:
            produced_timestamp = timestamp

    try:
        notice_set = {
            '_id': ObjectId(),
            '_created': timestamp,
            '_updated': timestamp,
            'feed_type': notice_data['feed_type'],
            'channel': notice_data['channel'],
            'message': notice_data['message'],
            'produced': produced_timestamp,
        }
    except:
        return (False, 'can not setup the notice')

    coll = db[collection]

    try:
        notice_id = coll.save(notice_set)
    except:
        return (False, 'can not save the notice data')

    return (True, {'_id': notice_id})

