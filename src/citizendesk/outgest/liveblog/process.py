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

'''
regarding SMS, liveblog creates them via GET requests, like
http://sourcefabric.superdesk.pro/resources/SMS/Inlet/other/Post/Push?phoneNumber=1234&messageText=hello+world
it creates a post, then if a blog subscribes to SMS feed, a (new) blogpost is created (for each subscribed blog)
'''
# this prefix is from a dust file
# https://github.com/superdesk/Live-Blog/blob/master/plugins/livedesk/gui-resources/templates/items/base.dust#L81
SMS_CONTENT_START = '<h3><a href="" target="_blank"></a></h3><div class="result-description"></div><!-- p.result-description tag displays for:> internal link> twitter> google link> google news> google images> flickr> youtube> soundcloud-->'
SMS_COMMENTS_META = {
    'annotation': {'before':None, 'after':None},
}

# for a tweet, the meta is the original tweet with the additions below
'''
https://github.com/superdesk/Live-Blog/blob/master/plugins/livedesk/gui-resources/scripts/js/providers/twitter.js#L204
adaptOldApiData : function(item) {
    item.profile_image_url = item.user.profile_image_url;
    item.from_user_name = item.user.name;
    item.from_user = item.user.screen_name;
    item.created_at_formated = item.created_at;
    item.api_version = '1.1';
    return item;
},
https://github.com/superdesk/Live-Blog/blob/master/plugins/livedesk/gui-resources/scripts/js/providers/twitter.js#L574
item.type = 'natural'
'''
TWT_COMMENTS_META = {
    'metadata': {'result_type':'', 'iso_language_code':''}, # this meta probably set by twitter
    'profile_image_url': '', # (http) twitter user profile image; ~1.0
    'from_user_name': '', # (real-like) name of twitter user; ~1.0
    'from_user': '', # screen/login name of twitter user; ~1.0
    'created_at_formated': '', # alike 'Mon Jun 30 13:16:50 +0000 2014'; ~1.0
    'api_version': '1.1', # ~1.0
    'type': 'natural', # probably for display purposes
    'annotation': {'before':None, 'after':None}, # local comments
}

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

    local: a text
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

    cursor = coll.find(search_spec).sort([(FIELD_UPDATED, 1)])
    for entry in cursor:
        for key in [FIELD_UPDATED, 'uuid', 'feed_type', 'texts']:
            if (key not in entry) or (not entry[key]):
                continue

        use_cid = cid_from_update(entry[FIELD_UPDATED])

        one_report = {
            'CId': entry['cid'],
            'IsPublished': True,
            'Uuid': entry['uuid'],
            'Type': {'Key': entry['feed_type']}
        }
        if (FIELD_DELETED in entry) and entry[FIELD_DELETED]:
            one_report['DeletedOn'] = entry[FIELD_DELETED]

        if entry['feed_type'] == 'SMS':
            entry['Meta'] = json.dumps({'before': 'this is a SMS', 'after': 'it may not be true'})

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

