#!/usr/bin/env python
#
# Citizen Desk
#

FIELD_TEXTS = 'texts'
FIELD_TEXTS_ORIGINAL = 'original'
FIELD_TEXTS_TRANSCRIPT = 'transcript'

from citizendesk.feeds.any.report.storage import FIELD_UPDATED as FIELD_UPDATED_REPORT
from citizendesk.feeds.any.report.storage import collection as COLL_REPORTS

# this is for loading the whole reports
schema = {
    '_id': 'ObjectID',
    'report_id': 'feed type-related string id',
    'parent_id': 'for linking among reports even when they are not stored (yet)',
    'session_id': 'grouping based on feed type-related ids',
}

