#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
import uuid

try:
    unicode
except:
    unicode = str

from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.feeds.any.report.storage import collection, schema, FIELD_UPDATED, FIELD_UUID
from citizendesk.feeds.any.report.storage import get_report_by_id, update_report_set
from citizendesk.feeds.any.coverage.storage import get_coverage_by_id

COVERAGE_SETS = ('targeting', 'published', 'outgested')

'''
coverages: {
    'targeting': [id_a, id_z],
    'published': [id_a, id_b],
    'outgested': [id_a, id_b, id_c],
}
'''

def do_publish_one(db, report_id, coverage_id=None):
    '''
    sets report as published in a coverage
    '''
    if not db:
        return (False, 'inner application error')

    report_id = _get_id_value(report_id)
    report_get = get_report_by_id(db, report_id)
    if not report_get[0]:
        return (False, 'report not found')
    report = report_get[1]

    if 'coverages' not in report:
        coverages = {}
        for cov_set in COVERAGE_SETS:
            coverages[cov_set] = []
        update_report_set(db, report_id, {'coverages': coverages})
        report['coverages'] = coverages

    coverages = report['coverages']
    if type(coverages) is not dict:
        return (False, 'report coverages not a dict')

    for cov_set in COVERAGE_SETS:
        if (cov_set not in coverages) or (type(coverages[cov_set]) is not list):
            return (False, 'report coverage parts missing or wrong')

    to_publish = coverages['targeting']

    if coverage_id:
        coverage_id = _get_id_value(coverage_id)
        coverage_get = get_coverage_by_id(db, coverage_id)
        if not coverage_get[0]:
            return (False, 'coverage not found')
        coverage_get = coverage_get[1]
        to_publish = [coverage_id]

    cov_published = coverages['published']
    cov_outgested = coverages['outgested']

    set_published = False
    set_outgested = False

    if not to_publish:
        return (False, 'no coverage to be published in')

    for one_cov in to_publish:
        if one_cov not in cov_published:
            set_published = True
            cov_published.append(one_cov)
        if one_cov not in cov_outgested:
            set_outgested = True
            cov_outgested.append(one_cov)

    if set_published:
        update_report_set(db, report_id, {'coverages.published': cov_published})
    if set_outgested:
        update_report_set(db, report_id, {'coverages.outgested': cov_outgested})

    timepoint = datetime.datetime.utcnow()
    adjective_set = {FIELD_UPDATED: timepoint}
    if FIELD_UUID not in report:
        adjective_set[FIELD_UUID] = str(uuid.uuid4().hex)
    update_report_set(db, report_id, adjective_set)

    return (True, {'_id': report_id})

def do_unpublish_one(db, report_id, coverage_id=None):
    '''
    sets report as unpublished in a coverage
    '''
    if not db:
        return (False, 'inner application error')

    report_id = _get_id_value(report_id)
    report_get = get_report_by_id(db, report_id)
    if not report_get[0]:
        return (False, 'report not found')
    report = report_get[1]

    if 'coverages' not in report:
        coverages = {}
        for cov_set in COVERAGE_SETS:
            coverages[cov_set] = []
        update_report_set(db, report_id, {'coverages': coverages})
        report['coverages'] = coverages

    coverages = report['coverages']
    if type(coverages) is not dict:
        return (False, 'report coverages not a dict')

    if ('published' not in coverages) or (type(coverages['published']) is not list):
        return (False, 'published coverages missing or wrong in report')

    cov_published = []

    if coverage_id:
        coverage_id = _get_id_value(coverage_id)
        if (coverage_id not in coverages['published']):
            return (False, 'not published into the coverage')
        for one_cov in coverages['published']:
            if one_cov != coverage_id:
                cov_published.append(one_cov)

    update_report_set(db, report_id, {'coverages.published': cov_published})

    timepoint = datetime.datetime.utcnow()
    adjective_set = {FIELD_UPDATED: timepoint}
    update_report_set(db, report_id, adjective_set)

    return (True, {'_id': report_id})

def do_on_behalf_of(db, report_id, user_id=None):
    '''
    un/sets report as on behalf of user
    '''
    if not db:
        return (False, 'inner application error')

    report_id = _get_id_value(report_id)
    report_get = get_report_by_id(db, report_id)
    if not report_get[0]:
        return (False, 'report not found')
    report = report_get[1]

    if user_id:
        user_id = _get_id_value(user_id)

    timepoint = datetime.datetime.utcnow()
    properties_set = {
        FIELD_UPDATED: timepoint,
        'on_behalf_id': user_id,
    }
    update_report_set(db, report_id, properties_set)

    return (True, {'_id': report_id})

