#!/usr/bin/env python
#
# Citizen Desk
#

COLL_COVERAGES = 'coverages'
COLL_REPORTS = 'reports'
FIELD_UPDATED = 'updated'
FIELD_DELETED = 'deleted'

from bson.objectid import ObjectId

import os, sys, datetime, json
from citizendesk.outgest.liveblog.utils import PUBLISHED_REPORTS_PLACEHOLDER
from citizendesk.outgest.liveblog.utils import get_conf, cid_from_update
from citizendesk.outgest.liveblog.adapts import adapt_sms_report, adapt_tweet_report, adapt_local_report

OUTPUT_FEED_TYPES = ['sms', 'tweet', 'plain']

def get_coverage_list(db, base_url):

    coll = db[COLL_COVERAGES]

    coverages = []

    cursor = coll.find({'active': True}, {'_id': True, 'title': True, 'description': True}).sort([('_id', 1)])

    for entry in cursor:
        cov_id = entry['_id']
        coverage_url = base_url.replace(PUBLISHED_REPORTS_PLACEHOLDER, cov_id)

        if 'title' not in entry:
            continue

        one_description = ''
        if ('description' in entry) and entry['description']:
            one_description = entry['description']

        one_cov = {
            'href': coverage_url,
            'Title': entry['title'],
            'Description': one_description,
        }
        coverages.append(one_cov)

    res = {
        'total': len(coverages),
        'limit': len(coverages),
        'offset': 0,
        'BlogList': coverages
    }

    return (True, res)

def get_coverage_published_report_list(db, coverage_id, update_last):
    '''
    SMS: original/transcribed text, can have two comments
    both creator and author are sms-based user/citizen, of smsblog source type (source name is name of sms feed)
    http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/854

    tweet: the original tweet (with some predefined adjusting), without any (other) changes, can have two comments
    creator is a local user, author is just the twitter source
    http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/855

    plain: a text
    http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/856

    other: ignoring by now
    '''


    citizen_url_template = get_conf('citizen_url')

    coll = db[COLL_REPORTS]

    reports = []

    try:
        coverage_id = ObjectID(coverage_id)
    except:
        pass

    search_spec = {
        'coverage': coverage_id,
        'published': True
    }
    if update_last:
        search_spec[FIELD_UPDATED] = {'gt': cid_last}

    # probably some adjusted dealing with: local, summary, unpublished/deleted reports

    cursor = coll.find(search_spec).sort([(FIELD_UPDATED, 1)])
    for entry in cursor:
        for key in [FIELD_UPDATED, 'uuid', 'feed_type', 'texts']:
            if (key not in entry) or (not entry[key]):
                continue

        feed_type = entry['feed_type']

        if feed_type not in OUTPUT_FEED_TYPES:
            continue

        content = None
        meta = None

        if 'sms' == feed_type:
            adapted = adapt_sms_report(entry)
            content = adapted['content']
            meta = adapted['meta']

        if 'tweet' == feed_type:
            adapted = adapt_tweet_report(entry)
            content = adapted['content']
            meta = adapted['meta']

        use_cid = cid_from_update(entry[FIELD_UPDATED])

        one_report = {
            'CId': use_cid,
            'IsPublished': True,
            'Uuid': entry['uuid'],
            'Type': {'Key': entry['feed_type']}
        }
        if (FIELD_DELETED in entry) and entry[FIELD_DELETED]:
            one_report['DeletedOn'] = entry[FIELD_DELETED]

        use_texts = []
        for one_text in entry['texts']:
            if one_text['translated']:
                use_texts.append(one_text['translated'])
                continue
            if one_text['original']:
                use_texts.append(one_text['original'])
        if not use_texts:
            continue

        one_reports['Content'] = '<div>' + '</div><div>'.join(use_texts) + '</div>'

        citizen_url = citizen_url_template.replace('<coverage_id>', cov_id)

        one_report['Author'] = {'href': citizen_url}
        one_report['Creator'] = {'href': citizen_url}

        reports.append(one_report)

    res = {
        'total': len(reports),
        'limit': len(reports),
        'offset': 0,
        'ReportList': reports
    }

    return (True, res)

def get_citizen(form):
    if form not in ['author', 'creator']:
        return (False, 'unknown citizen form')

    return {
        'Source': {'Name': None},
        'Uuid': None,
        'Cid': None
    }

