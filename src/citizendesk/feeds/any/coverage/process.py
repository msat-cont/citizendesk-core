#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_sort as _get_sort
from citizendesk.common.utils import get_etag as _get_etag
from citizendesk.feeds.any.coverage.storage import collection, schema, FIELD_ACTIVE, FIELD_DECAYED
from citizendesk.feeds.any.coverage.storage import get_coverage_by_id, update_coverage_set
from citizendesk.feeds.any.report.storage import collection as collection_reports
from citizendesk.feeds.any.report.storage import FIELD_COVERAGES_PUBLISHED
from citizendesk.feeds.any.report.storage import FIELD_UPDATED as FIELD_UPDATED_REPORT

DEFAULT_LIMIT = 20

def do_get_one(db, coverage_id):
    '''
    returns data of a single coverage
    '''
    if not db:
        return (False, 'inner application error')

    coverage_id = _get_id_value(coverage_id)
    res = get_coverage_by_id(db, coverage_id)

    return res

def do_get_list(db, offset, limit, sort, other):
    '''
    returns list of coverages
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {}

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
            if 'title' not in entry:
                continue

            one_name = {
                'title': entry['title'],
                FIELD_ACTIVE: None,
            }

            if FIELD_ACTIVE in entry:
                one_name[FIELD_ACTIVE] = entry[FIELD_ACTIVE]

            docs.append(one_name)

    return (True, docs, {'total': total})

def do_insert_one(db, coverage_data):
    '''
    creates a coverage
    '''
    if not db:
        return (False, 'inner application error')

    timepoint = datetime.datetime.utcnow()

    try:
        coverage_set = {
            'title': str(coverage_data['title']),
            'description': str(coverage_data['description']),
            'user_id': _get_id_value(coverage_data['user_id']),
            FIELD_ACTIVE: False,
            FIELD_DECAYED: False,
            '_created': timepoint,
            '_updated': timepoint,
            '_etag': _get_etag(),
        }
    except:
        return (False, 'can not setup the coverage')

    if ('active' in coverage_data) and (coverage_data['active']):
        coverage_set[FIELD_ACTIVE] = True

    coll = db[collection]

    try:
        coverage_id = coll.save(coverage_set)
    except:
        return (False, 'can not save the coverage data')

    return (True, {'_id': coverage_id})

def do_set_active_one(db, coverage_id, set_active):
    '''
    de/activate a coverage
    '''
    if not db:
        return (False, 'inner application error')

    coverage_id = _get_id_value(coverage_id)
    coverage_get = get_coverage_by_id(db, coverage_id)
    if not coverage_get[0]:
        return (False, 'coverage not found')
    coverage = coverage_get[1]

    if set_active:
        if (FIELD_DECAYED in coverage) and coverage[FIELD_DECAYED]:
            return (False, 'can not activate decayed coverage')

    timepoint = datetime.datetime.utcnow()

    update_coverage_set(db, coverage_id, {FIELD_ACTIVE: set_active, '_updated': timepoint})

    return (True, {'_id': coverage_id})

def do_unpublish_one(db, coverage_id):
    '''
    unpublish all reports from a coverage
    '''
    if not db:
        return (False, 'inner application error')

    coverage_id = _get_id_value(coverage_id)
    timepoint = datetime.datetime.utcnow()

    update_set = {
        FIELD_UPDATED_REPORT: timepoint,
        '_etag': _get_etag(),
    }
    excise_set = {FIELD_COVERAGES_PUBLISHED: [coverage_id]}

    coll = db[collection_reports]
    coll.update({FIELD_COVERAGES_PUBLISHED: coverage_id}, {'$pullAll': excise_set, '$set': update_set}, multi=True, upsert=False)

    return (True, {'_id': coverage_id})

