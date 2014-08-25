#!/usr/bin/env python
#
# Citizen Desk
#

from bson.objectid import ObjectId
from citizendesk.common.utils import get_id_value as _get_id_value

import os, sys, datetime, json, urllib

COLL_USERS = 'users'
COLL_COVERAGES = 'coverages'
COLL_REPORTS = 'reports'

from citizendesk.feeds.any.report.storage import FIELD_UPDATED as FIELD_UPDATED_REPORT
from citizendesk.feeds.any.report.storage import FIELD_DECAYED as FIELD_DECAYED_REPORT
from citizendesk.feeds.any.report.storage import FIELD_UUID as FIELD_UUID_REPORT
from citizendesk.feeds.any.report.storage import FIELD_PUTUP as FIELD_PUTUP_REPORT

FIELD_UPDATED_USER = '_updated'

from citizendesk.feeds.any.coverage.storage import FIELD_ACTIVE as FIELD_ACTIVE_COVERAGE
from citizendesk.feeds.any.coverage.storage import FIELD_DECAYED as FIELD_DECAYED_COVERAGE

def load_local_user(db, user_id):

    user_id = _get_id_value(user_id)

    coll = db[COLL_USERS]

    user = coll.find_one({'_id': user_id})
    if not user:
        return None

    return user

