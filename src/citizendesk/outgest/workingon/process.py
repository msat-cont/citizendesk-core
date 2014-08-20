#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json, urllib
from citizendesk.outgest.workingon.utils import get_conf, PARAGRAPH_TEXTS_SEPARATOR
from citizendesk.outgest.workingon.storage import COLL_REPORTS, FIELD_UPDATED_REPORT
from citizendesk.outgest.workingon.storage import FIELD_TEXTS, FIELD_TEXTS_ORIGINAL, FIELD_TEXTS_TRANSCRIPT
from citizendesk.outgest.workingon.storage import schema
from citizendesk.common.utils import get_sort as _get_sort

DEFAULT_LIMIT = 20

def get_workingon_reports_list(db, offset=None, limit=None, sort=None):
    '''
    returns texts of reports that have been worked on
    '''
    if not db:
        return (False, 'inner application error')

    field_public_report = get_conf('field_public_report')
    condition_public_report = get_conf('condition_public_report')

    sort_list = _get_sort(sort)
    if not sort_list:
        sort_list = [(FIELD_UPDATED_REPORT, -1)]

    search_conditions = {
        field_public_report: condition_public_report,
        FIELD_TEXTS: {'$exists': True, '$not': {'$size': 0}},
    }

    coll = db[COLL_REPORTS]
    cursor = coll.find(search_conditions, {FIELD_TEXTS: True}).sort(sort_list)
    total = cursor.count()

    if limit is None:
        limit = DEFAULT_LIMIT

    if offset:
        cursor = cursor.skip(offset)
    if limit:
        cursor = cursor.limit(limit)

    texts = []
    for entry in cursor:
        entry_texts = []

        if FIELD_TEXTS not in entry:
            continue
        if type(entry[FIELD_TEXTS]) not in (list, tuple):
            continue
        for one_text_part in entry[FIELD_TEXTS]:
            cur_text = ''
            if type(one_text_part) is not dict:
                continue
            if (FIELD_TEXTS_ORIGINAL in one_text_part) and (one_text_part[FIELD_TEXTS_ORIGINAL]):
                cur_text = one_text_part[FIELD_TEXTS_ORIGINAL]
            if (FIELD_TEXTS_TRANSCRIPT in one_text_part) and (one_text_part[FIELD_TEXTS_TRANSCRIPT]):
                cur_text = one_text_part[FIELD_TEXTS_TRANSCRIPT]
            if cur_text:
                entry_texts.append(cur_text)

        if entry_texts:
            texts.append(PARAGRAPH_TEXTS_SEPARATOR.join(entry_texts))

    return (True, texts, {'total': total})
