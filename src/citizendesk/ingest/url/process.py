#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, datetime, json
import datetime

from citizendesk.ingest.url.utils import citizen_holder, report_holder
from citizendesk.ingest.url.utils import get_conf
from citizendesk.ingest.url.eff_tlds import take_specific_domain
from citizendesk.ingest.url.url_info import get_page_info
from citizendesk.common.utils import get_logger

try:
    from urllib.parse import urlparse, urlunparse, urljoin
except:
    from urlparse import urlparse, urlunparse, urljoin

def assure_citizen_alias(db, authority, use_identifiers, author_name):
    ''' create citizen alias if does not exist yet '''

    found_aliases = citizen_holder.alias_present(authority, 'user_id_search', use_identifiers['user_id_search'])
    if found_aliases:
        return (True, citizen_alias[0]['_id'])

    alias_new = {
        'authority': authority,
        'identifiers': use_identifiers,
        'verified': False,
        'local': False
    }
    if author_name:
        alias_new['full_name'] = author_name

    alias_id = citizen_holder.save_alias(alias_new)
    if not alias_id:
        return (False, 'can not save citizen alias info')

    return (True, alias_id)

def do_post(db, url, channel_type, request_id, client_ip):
    '''
    * assure citizen_alias exists (i.e. create/save if does not yet)
    * create and save the report
    * channel_type: frontend, bookmarklet, etc.
    '''
    logger = get_logger()

    timestamp = datetime.datetime.utcnow()

    if not url:
        return (False, 'emtpy url')
    try:
        url = url.strip()
        url_parsed = urlparse(url, scheme='http')
    except:
        url_parsed = None
    if not url_parsed:
        return (False, 'can not parse the url')
    if not url_parsed.netloc:
        return (False, 'url without domain part')

    # taking params
    feed_type = get_conf('feed_type')
    eff_tlds = get_conf('eff_tlds')

    # taking info
    if eff_tlds:
        citizen_id = take_specific_domain(eff_tlds, url_parsed.netloc.split(':')[0].strip())
    else:
        citizen_id = url_parsed.netloc.split(':')[0].strip()
    if not citizen_id:
        citizen_id = url

    page_info_got = get_page_info(url)
    if not page_info_got[0]:
        return (False, 'can not get page info: ' + page_info_got[1])
    page_info = page_info_got[1]

    report_id = report_holder.gen_id(feed_type)

    session_url = ''
    if ('url' in page_info) and page_info['url']:
        try:
            session_url = page_info['url'].split('#')[0].strip().lower()
        except:
            pass
    if not session_url:
        session_url = url.split('#')[0].strip().lower()
    session = feed_type + '||' + session_url

    source_url = ''
    if ('url' in page_info) and page_info['url']:
        try:
            source_url = page_info['url'].strip()
        except:
            pass
    if not source_url:
        source_url = url.strip()

    parent_id = None
    publisher = None

    if ('feed_name' in page_info) and page_info['feed_name']:
        feed_name = page_info['feed_name']
    else:
        feed_name = None

    use_language = None
    if ('language' in page_info) and page_info['language']:
        use_language = page_info['language']

    authority = get_conf('authority')
    use_identifiers = {
        'user_id': citizen_id,
        'user_id_search': citizen_id.lower(),
        'user_name': citizen_id,
        'user_name_search': citizen_id.lower(),
    }

    channel_value = None
    if ('type' in page_info) and page_info['type']:
        try:
            channel_value = page_info['type'].strip().lower()
            if not channel_value:
                channel_value = None
        except:
            channel_value = None

    channels = [{'type': channel_type, 'value': channel_value, 'filter': None, 'request': request_id, 'reasons': None}]
    authors = [{'authority': authority, 'identifiers': use_identifiers}]

    author_name = ''
    if 'author' in page_info:
        author_name = page_info['author']
    alias_res_got = assure_citizen_alias(db, authority, use_identifiers, author_name)

    endorsers = []
    original = page_info
    original_id = url # notice that we group the (effective) URLs via session
    tags = []

    texts = []
    text_parts = ['title', 'description']
    for one_text_part in text_parts:
        if (one_text_part in page_info) and page_info[one_text_part]:
            texts.append({'original': page_info[one_text_part], 'transcript': None})

    estimated = timestamp
    if ('date' in page_info) and page_info['date'] and (type(page_info['date']) is datetime.datetime):
        estimated = page_info['date']

    # site_icon added at the end of the media list
    media = []
    if ('image' in page_info) and page_info['image'] and (type(page_info['image']) in (list, tuple)):
        for one_image_link in page_info['image']:
            try:
                link_ssl = None
                if one_image_link.startswith('https'):
                    link_ssl = one_image_link
                media.append({
                    'link': one_image_link,
                    'link_ssl': link_ssl,
                    'data': None,
                    'name': None,
                    'width': None,
                    'height': None,
                })
            except:
                pass

    if ('site_icon' in page_info) and page_info['site_icon']:
        try:
            link_ssl = None
            if page_info['site_icon'].startswith('https'):
                link_ssl = page_info['site_icon']
            media.append({
                'link': page_info['site_icon'],
                'link_ssl': link_ssl,
                'data': None,
                'name': None,
                'width': None,
                'height': None,
            })
        except:
            pass

    report = {}
    report['report_id'] = report_id
    report['parent_id'] = None
    report['client_ip'] = client_ip
    report['feed_type'] = feed_type
    report['produced'] = estimated
    report['session'] = session
    report['publisher'] = publisher
    report['channels'] = channels
    report['authors'] = authors
    report['original'] = original
    report['texts'] = texts
    report['tags'] = tags
    report['language'] = use_language
    report['sources'] = [source_url]
    report['media'] = media

    report['proto'] = False

    report_doc_id = report_holder.save_report(report)
    if not report_doc_id:
        return (False, 'can not save URL report')

    return (True, {'_id': report_doc_id})

