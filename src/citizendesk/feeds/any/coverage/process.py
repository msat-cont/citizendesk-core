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
from citizendesk.feeds.any.report.coverage import collection, schema, FIELD_ACTIVE, FIELD_DECAYED
from citizendesk.feeds.any.report.coverage import get_coverage_by_id, update_coverage_set

def do_insert_one(db, coverage_data):
    '''
    creates a coverage
    '''
    if not db:
        return (False, 'inner application error')

    try:
        coverage_set = {
            'title': str(coverage_data['title']),
            'description': str(coverage_data['description']),
            'user_id': _get_id_value(coverage_data['user_id']),
            'is_active': False,
            'is_decayed': False,
        }
    except:
        return (False, 'can not setup the report')

    if ('active' in coverage_data) and (coverage_data['active']):
        coverage_set['is_active'] = True

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

    update_coverage_set(db, coverage_id, {FIELD_ACTIVE: set_active})

    return (True, {'_id': coverage_id})

