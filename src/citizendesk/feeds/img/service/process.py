#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

import os, sys, time, datetime
import urllib

from citizendesk.common.utils import get_id_value as _get_id_value
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_sort as _get_sort
from citizendesk.common.utils import get_etag as _get_etag
from citizendesk.feeds.img.service.storage import collection, schema, FIELD_ACTIVE
from citizendesk.feeds.img.service.storage import METHOD_CLIENT_GET, SERVICE_IMAGE_TYPE, URL_ENCODED_IMG_LINK
from citizendesk.feeds.img.service.storage import get_service_by_id, update_service_set
from citizendesk.feeds.any.report.storage import get_report_by_id, FIELD_MEDIA, MEDIA_IMAGE_TYPE

DEFAULT_LIMIT = 20

def do_get_resolved(db, report_id):
    '''
    returns resolved methods on media of a single report
    '''
    if not db:
        return (False, 'inner application error')

    sort_list = [('_id',1)]

    coll = db[collection]
    cursor = coll.find().sort(sort_list)
    services = []
    for entry in cursor:
        if not entry:
            continue
        entry_use = {
            '_id': entry['_id'],
        }
        try:
            if not 'type' in entry:
                continue
            if entry['type'] != SERVICE_IMAGE_TYPE:
                continue
            if (FIELD_ACTIVE not in entry) or (not entry[FIELD_ACTIVE]):
                continue
            if not 'spec' in entry:
                continue
            spec = entry['spec']
            if ('method' not in spec) or (not spec['method']):
                continue
            if spec['method'] != METHOD_CLIENT_GET:
                continue

            link_http = None
            link_https = None
            if ('http' in spec) and spec['http']:
                link_http = spec['http']
            if ('https' in spec) and spec['https']:
                link_https = spec['https']
            if (not link_http) and (not link_https):
                continue
            if not link_http:
                link_http = link_https
            if not link_https:
                link_https = link_http
            entry_use['link'] = link_http
            entry_use['link_ssl'] = link_https

            if ('parameters' not in spec) or (not spec['parameters']):
                continue
            if type(spec['parameters']) is not dict:
                continue
            known_parameters = True
            for one_param in spec['parameters']:
                if spec['parameters'][one_param] != URL_ENCODED_IMG_LINK:
                    known_parameters = False
                    break
            if not known_parameters:
                continue
            entry_use['parameters'] = spec['parameters']
        except Exception as exc:
            continue

        services.append(entry_use)

    report_id = _get_id_value(report_id)
    res = get_report_by_id(db, report_id)
    if not res[0]:
        return res

    report = res[1]
    if type(report) is not dict:
        return (False, 'unknown structure of report')

    if (FIELD_MEDIA not in report) or (not report[FIELD_MEDIA]):
        return (True, [])

    if type(report[FIELD_MEDIA]) not in (list, tuple):
        return (False, 'unknown structure of report media list')

    media_services = []
    for one_media in report[FIELD_MEDIA]:
        one_link_set = {}
        if (type(one_media) is not dict):
            media_services.append(one_link_set)
            continue
        if ('type' in one_media) and (one_media['type'] != MEDIA_IMAGE_TYPE):
            media_services.append(one_link_set)
            continue

        link = None
        link_ssl = None
        if ('link' in one_media) and (one_media['link']):
            link = one_media['link']
        if ('link_ssl' in one_media) and (one_media['link_ssl']):
            link_ssl = one_media['link_ssl']
        if (not link) and (not link_ssl):
            media_services.append(one_link_set)
            continue
        if not link:
            link = link_ssl
        if not link_ssl:
            link_ssl = link
        link = urllib.quote_plus(link)
        link_ssl = urllib.quote_plus(link_ssl)

        try:
            for one_service in services:
                one_id = str(one_service['_id'])
                one_link = one_service['link']
                one_link_ssl = one_service['link_ssl']
                for one_param in one_service['parameters']:
                    one_link = one_link.replace(one_param, link)
                    one_link_ssl = one_link_ssl.replace(one_param, link_ssl)
                one_link_set[one_id] = {
                    'link': one_link,
                    'link_ssl': one_link_ssl,
                }
        except Exception as exc:
            pass

        media_services.append(one_link_set)

    return (True, media_services)

def do_get_one(db, service_id):
    '''
    returns data of a single service
    '''
    if not db:
        return (False, 'inner application error')

    service_id = _get_id_value(service_id)
    res = get_service_by_id(db, service_id)

    return res

def do_get_list(db, offset, limit, sort, other):
    '''
    returns list of services
    '''
    if not db:
        return (False, 'inner application error')

    list_spec = {}

    sort_list = _get_sort(sort)
    if not sort_list:
        sort_list = [('produced', 1)]

    name_only = False
    if other and ('name_only' in other) and other['name_only']:
        try:
            name_only = bool(_get_boolean(other['name_only']))
        except:
            name_only = False

    coll = db[collection]
    cursor = coll.find(list_spec).sort(sort_list)

    total = cursor.count()

    if limit is None:
        limit = DEFAULT_LIMIT

    if offset:
        cursor = cursor.skip(offset)
    if limit:
        cursor = cursor.limit(limit)

    docs = []
    for entry in cursor:
        if not entry:
            continue
        if not name_only:
            docs.append(entry)
        else:
            if 'title' not in entry:
                continue

            one_name = {
                'title': entry['title'],
                FIELD_ACTIVE: None,
            }

            if FIELD_ACTIVE in entry:
                one_name[FIELD_ACTIVE] = entry[FIELD_ACTIVE]

            docs.append(one_name)

    return (True, docs, {'total': total})

def do_insert_one(db, service_data):
    '''
    creates a service
    '''
    if not db:
        return (False, 'inner application error')

    if type(service_data['spec']) is not dict:
        return (False, 'wrong spec structure')

    timepoint = datetime.datetime.utcnow()

    try:
        service_set = {
            'key': unicode(service_data['key']),
            'site': unicode(service_data['site']),
            'title': unicode(service_data['title']),
            'description': unicode(service_data['description']),
            'type': unicode(service_data['type']),
            'spec': service_data['spec'],
            'notice': '',
            FIELD_ACTIVE: False,
            '_created': timepoint,
            '_updated': timepoint,
            #'_etag': _get_etag(),
        }
    except:
        return (False, 'can not setup the service')

    if ('notice' in service_data) and (service_data['notice']):
        service_set['notice'] = service_data['notice']
    if ('active' in service_data) and (service_data['active']):
        service_set[FIELD_ACTIVE] = True

    coll = db[collection]

    try:
        service_id = coll.save(service_set)
    except:
        return (False, 'can not save the service data')

    return (True, {'_id': service_id})

def do_set_active_one(db, service_id, set_active):
    '''
    de/activate a service
    '''
    if not db:
        return (False, 'inner application error')

    service_id = _get_id_value(service_id)
    service_get = get_service_by_id(db, service_id)
    if not service_get[0]:
        return (False, 'service not found')
    service = service_get[1]

    timepoint = datetime.datetime.utcnow()

    update_service_set(db, service_id, {FIELD_ACTIVE: set_active, '_updated': timepoint})

    return (True, {'_id': service_id})

def do_delete_one(db, service_id):
    '''
    remove one service
    '''
    if not db:
        return (False, 'inner application error')

    service_id = _get_id_value(service_id)
    service_get = get_service_by_id(db, service_id)
    if not service_get[0]:
        return (False, 'service not found')
    service = service_get[1]

    coll = db[collection]
    cursor = coll.remove({'_id': service_id})

    return (True, {'_id': service_id})
