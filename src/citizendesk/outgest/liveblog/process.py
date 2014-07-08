#!/usr/bin/env python
#
# Citizen Desk
#

from bson.objectid import ObjectId

import os, sys, datetime, json, urllib
from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.outgest.liveblog.utils import COVERAGE_PLACEHOLDER, PUBLISHED_REPORTS_PLACEHOLDER, REPORT_LINK_ID_PLACEHOLDER
from citizendesk.outgest.liveblog.utils import get_conf, cid_from_update, update_from_cid
from citizendesk.outgest.liveblog.adapts import adapt_sms_report, adapt_tweet_report, adapt_plain_report
from citizendesk.outgest.liveblog.adapts import get_sms_report_author, get_tweet_report_author, get_plain_report_author
from citizendesk.outgest.liveblog.storage import COLL_COVERAGES, COLL_REPORTS, FIELD_UPDATED, FIELD_DELETED

OUTPUT_FEED_TYPES = ['sms', 'tweet', 'plain']

def get_coverage_list(db):

    base_url = get_conf('coverage_info_url')

    coll = db[COLL_COVERAGES]

    coverages = []

    cursor = coll.find({'active': True}, {'_id': True, 'title': True, 'description': True}).sort([('_id', 1)])

    for entry in cursor:
        cov_id = entry['_id']
        coverage_url = base_url.replace(COVERAGE_PLACEHOLDER, urllib.quote_plus(str(cov_id)))

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

def get_coverage_info(db, coverage_id):

    coverage_id = _get_id_value(coverage_id)

    coll = db[COLL_COVERAGES]
    coverage = coll.find_one({'_id': coverage_id})
    if not coverage:
        return (False, 'coverage not found')

    base_url = get_conf('reports_url')
    reports_url = base_url.replace(PUBLISHED_REPORTS_PLACEHOLDER, urllib.quote_plus(str(coverage_id)))

    title = ''
    if ('title' in coverage) and coverage['title']:
        title = coverage['title']
    description = ''
    if ('description' in coverage) and coverage['description']:
        description = coverage['description']
    active = False
    if ('active' in coverage) and coverage['active']:
        active = coverage['active']

    info = {
        'IsLive': active,
        'Title': title,
        'Description': description,
        'PostPublished': {'href': reports_url,},
    }

    return (True, info)

def get_coverage_published_report_list(db, coverage_id, cid_last):
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

    author_url_template = get_conf('author_url')
    creator_url_template = get_conf('creator_url')

    coll = db[COLL_REPORTS]

    reports = []

    try:
        coverage_id = _get_id_value(coverage_id)
    except:
        pass

    search_spec = {
        'coverage': coverage_id,
        'published': True
    }
    if cid_last:
        update_last = update_from_cid(cid_last)
        search_spec[FIELD_UPDATED] = {'gt': update_last}

    # probably some adjusted dealing with: local, summary, unpublished/deleted reports

    cursor = coll.find(search_spec).sort([(FIELD_UPDATED, 1)])
    for entry in cursor:
        with_fields = True
        for key in [FIELD_UPDATED, 'uuid', 'feed_type', 'texts']:
            if (key not in entry) or (not entry[key]):
                with_fields = False
                break
        #if not with_fields:
        #    continue

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

        if 'plain' == feed_type:
            adapted = adapt_plain_report(entry)
            content = adapted['content']
            meta = adapted['meta']

        use_cid = 0
        if FIELD_UPDATED in entry:
            use_cid = cid_from_update(entry[FIELD_UPDATED])

        one_report = {
            'CId': use_cid,
            'IsPublished': 'True',
            'Type': {'Key': 'normal'},
            'Content': content,
            'Meta': meta,
        }

        if 'uuid' in entry:
            one_report['uuid'] = entry['uuid']

        if (FIELD_DELETED in entry) and entry[FIELD_DELETED]:
            one_report['DeletedOn'] = entry[FIELD_DELETED]

        link_id = urllib.quote_plus(str(entry['_id']))
        author_url = author_url_template.replace(REPORT_LINK_ID_PLACEHOLDER, link_id)
        creator_url = creator_url_template.replace(REPORT_LINK_ID_PLACEHOLDER, link_id)

        one_report['Author'] = {'href': author_url}
        one_report['Creator'] = {'href': creator_url}

        reports.append(one_report)

    res = {
        'total': len(reports),
        'limit': len(reports),
        'offset': 0,
        'PostList': reports
    }

    return (True, res)

def get_report_author(db, report_id, author_form):

    coll = db[COLL_REPORTS]

    if author_form not in ['author', 'creator']:
        return (False, 'unknown author form')

    report_id = _get_id_value(report_id)
    report = coll.find_one({'_id': report_id})
    if not report:
        return (False, 'respective report not found')

    if 'feed_type' not in report:
        return (False, 'feed type not set in the respective report')

    feed_type = report['feed_type']

    if feed_type not in OUTPUT_FEED_TYPES:
        return (False, 'unsupported report type')

    author = None

    if 'sms' == feed_type:
        if 'author' == author_form:
            author = get_sms_report_author(report)
        if 'creator' == author_form:
            author = get_sms_report_creator(report)

    if 'tweet' == feed_type:
        if 'author' == author_form:
            author = get_tweet_report_author(report)
        if 'creator' == author_form:
            author = get_tweet_report_creator(report)

    if 'plain' == feed_type:
        if 'author' == author_form:
            author = get_plain_report_author(report)
        if 'creator' == author_form:
            author = get_plain_report_creator(report)

    return (True, author)

