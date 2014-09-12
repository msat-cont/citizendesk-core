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
from citizendesk.outgest.liveblog.adapts import get_sms_report_creator, get_tweet_report_creator, get_plain_report_creator
from citizendesk.outgest.liveblog.adapts import get_sms_report_icon, get_tweet_report_icon, get_plain_report_icon
from citizendesk.outgest.liveblog.storage import load_local_user
from citizendesk.outgest.liveblog.storage import COLL_COVERAGES, COLL_REPORTS
from citizendesk.outgest.liveblog.storage import FIELD_UPDATED_REPORT, FIELD_DECAYED_REPORT, FIELD_UUID_REPORT, FIELD_PUTUP_REPORT
from citizendesk.outgest.liveblog.storage import FIELD_ACTIVE_COVERAGE

OUTPUT_FEED_TYPES = ['sms', 'tweet', 'plain']
DEFAULT_FIELD_TYPE = 'plain'

def get_coverage_list(db):

    base_url = get_conf('coverage_info_url')

    coll = db[COLL_COVERAGES]

    coverages = []

    cursor = coll.find({FIELD_ACTIVE_COVERAGE: True}, {'_id': True, 'title': True, 'description': True, 'uuid': True}).sort([('_id', 1)])

    for entry in cursor:
        if 'uuid' not in entry:
            continue

        cov_id = entry['uuid']
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

    if type(coverage_id) is ObjectId:
        return (False, 'old form of coverage info retrieval')
    else:
        coverage = coll.find_one({'uuid': coverage_id})

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
    if (FIELD_ACTIVE_COVERAGE in coverage) and coverage[FIELD_ACTIVE_COVERAGE]:
        active = coverage[FIELD_ACTIVE_COVERAGE]

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
    try:
        coverage_id = _get_id_value(coverage_id)
    except:
        pass

    res_none = {
        'total': 0,
        'limit': 0,
        'offset': 0,
        'PostList': []
    }

    coll = db[COLL_COVERAGES]

    if type(coverage_id) is ObjectId:
        return (False, 'old form of coverage reports retrieval')
    else:
        coverage = coll.find_one({'uuid': coverage_id})

    if not coverage:
        return (False, 'coverage not found')
    if (FIELD_ACTIVE_COVERAGE not in coverage) or (not coverage[FIELD_ACTIVE_COVERAGE]):
        return (True, res_none)

    author_url_template = get_conf('author_url')
    creator_url_template = get_conf('creator_url')

    coll = db[COLL_REPORTS]

    reports = []

    put_up_border = datetime.datetime.utcfromtimestamp(0)

    search_spec = {
        'coverages.outgested': {'$in': [coverage_id, coverage['_id']]},
        FIELD_DECAYED_REPORT: {'$ne': True},
    }
    if cid_last:
        update_last = update_from_cid(cid_last)
        search_spec[FIELD_UPDATED_REPORT] = {'$gt': update_last}
        put_up_border = update_last
    else:
        search_spec[FIELD_UPDATED_REPORT] = {'$exists': True}

    # probably some adjusted dealing with: local, summary, unpublished/deleted reports
    cursor = coll.find(search_spec).sort([(FIELD_UPDATED_REPORT, 1)])
    for entry in cursor:
        if 'feed_type' not in entry:
            entry['feed_type'] = DEFAULT_FIELD_TYPE

        with_fields = True
        for key in [FIELD_UPDATED_REPORT, FIELD_UUID_REPORT, 'feed_type', 'texts', 'coverages']:
            if (key not in entry) or (not entry[key]):
                with_fields = False
                break
        if not with_fields:
            continue
        if type(entry['coverages']) is not dict:
            continue
        if ('published' not in entry['coverages']):
            continue
        if type(entry['coverages']['published']) not in (list, tuple):
            continue

        feed_type = entry['feed_type']

        if feed_type not in OUTPUT_FEED_TYPES:
            continue

        content = None
        meta = None

        if 'sms' == feed_type:
            adapted = adapt_sms_report(db, entry)
            content = adapted['content']
            meta = adapted['meta']

        if 'tweet' == feed_type:
            adapted = adapt_tweet_report(db, entry)
            content = adapted['content']
            meta = adapted['meta']

        if 'plain' == feed_type:
            adapted = adapt_plain_report(db, entry)
            content = adapted['content']
            meta = adapted['meta']

        use_cid = 0
        if FIELD_UPDATED_REPORT in entry:
            use_cid = cid_from_update(entry[FIELD_UPDATED_REPORT])

        one_report = {
            'CId': use_cid,
            'IsPublished': 'True',
            'Type': {'Key': 'normal'},
            'Content': content,
            'Meta': meta,
        }

        if FIELD_UUID_REPORT in entry:
            one_report['Uuid'] = entry[FIELD_UUID_REPORT]

        if (FIELD_PUTUP_REPORT in entry) and entry[FIELD_PUTUP_REPORT]:
            try:
                if entry[FIELD_PUTUP_REPORT] > put_up_border:
                    one_report['PutUp'] = 'True'
            except:
                pass

        if coverage_id not in entry['coverages']['published']:
            if coverage['_id'] not in entry['coverages']['published']:
                one_report['DeletedOn'] = '01/01/70 12:01 AM'

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

    if author_form not in ['author', 'creator', 'icon']:
        return (False, 'unknown author form')

    report_id = _get_id_value(report_id)
    report = coll.find_one({'_id': report_id})
    if not report:
        return (False, 'respective report not found')

    if 'feed_type' not in report:
        report['feed_type'] = DEFAULT_FIELD_TYPE

    feed_type = report['feed_type']

    if feed_type not in OUTPUT_FEED_TYPES:
        return (False, 'unsupported report type')

    author = None

    user = None
    if 'on_behalf_id' in report:
        user_id = report['on_behalf_id']
        user = load_local_user(db, user_id)
    if not user:
        user = None

    if 'sms' == feed_type:
        if 'author' == author_form:
            author = get_sms_report_author(report_id, report, user)
        if 'creator' == author_form:
            author = get_sms_report_creator(report_id, report, user)
        if 'icon' == author_form:
            author = get_sms_report_icon(report_id, report, user)

    if 'tweet' == feed_type:
        if 'author' == author_form:
            author = get_tweet_report_author(report_id, report, user)
        if 'creator' == author_form:
            author = get_tweet_report_creator(report_id, report, user)
        if 'icon' == author_form:
            author = get_tweet_report_icon(report_id, report, user)

    if 'plain' == feed_type:
        if 'author' == author_form:
            author = get_plain_report_author(report_id, report, user)
        if 'creator' == author_form:
            author = get_plain_report_creator(report_id, report, user)
        if 'icon' == author_form:
            author = get_plain_report_icon(report_id, report, user)

    return (True, author)
