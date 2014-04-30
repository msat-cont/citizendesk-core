#!/usr/bin/env python
#
# Citizen Desk
#

COLL_COVERAGES = 'coverages'
COLL_POSTS = 'reports'

import os, sys, datetime, json
from citizendesk.ingest.twt.connect import get_conf, gen_id, get_tweet

def get_coverage_list(db):

    coverage_url_template = get_config('coverage_url')

    coll = db[COLL_COVERAGES]

    coverages = []

    cursor = coll.find({'active': True}, {'_id': True, 'title': True, 'description': True}).sort([('_id', 1)])

    for entry in cursor:
        cov_id = entry['_id']
        coverage_url = coverage_url_template.replace('<coverage_id>', cov_id)
        one_cov = {
            'href': coverage_url,
            'Title': entry['title'],
            'Description': entry['description']
        }
        coverages.append(one_cov)

    res = {
        'total': len(coverages),
        'limit': len(coverages),
        'offset': 0,
        'BlogList': coverages
    }

    return (True, res)

def get_coverage_published_post_list(db, coverage_id, cid_last):

    citizen_url_template = get_config('citizen_url')

    coll = db[COLL_POSTS]

    posts = []

    try:
        coverage_id = ObjectID(coverage_id)
    except:
        pass

    search_spec = {
        'coverage': coverage_id,
        'published': True
    }
    if cid_last:
        try:
            cid_last = int(cid_last)
        except:
            return (False, 'change id is not an integer')
        search_spec['cid'] = {'gt': cid_last}

    cursor = coll.find(search_spec).sort([('cid', 1)])
    for entry in cursor:
        for key in ['cid', 'uuid', 'feed_type', 'texts']:
            if (key not in entry) or (not entry[key]):
                continue

        one_post = {
            'CId': entry['cid'],
            'IsPublished': True,
            'Uuid': entry['uuid'],
            'Type': {'Key': entry['feed_type']}
        }
        if ('deleted' in entry) and entry['deleted']:
            one_post['DeletedOn'] = entry['deleted']

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

        one_posts['Content'] = '<div>' + '</div><div>'.join(use_texts) + '</div>'

        citizen_url = citizen_url_template.replace('<coverage_id>', cov_id)

        one_post['Author'] = {'href': citizen_url}
        one_post['Creator'] = {'href': citizen_url}

        posts.append(one_post)

    res = {
        'total': len(posts),
        'limit': len(posts),
        'offset': 0,
        'PostList': posts
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

