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

#FIELD_UPDATED = '_updated'
FIELD_UPDATED = 'updated'
FIELD_DELETED = 'unpublished'

def load_local_user(user_id):

    user_id = _get_id_value(user_id)

    coll = db[COLL_USERS]

    user = coll.find_one({'_id': user_id})
    if not user:
        return None

    return user

