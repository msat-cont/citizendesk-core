#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
try:
    from citizendesk.feeds.twt.external import newstwister as controller
except:
    controller = None

try:
    unicode
except:
    unicode = str

from bson.objectid import ObjectId

from citizendesk.feeds.twt.authorized.storage import collection, schema, get_one, USE_SEQUENCES
from citizendesk.common.utils import get_id_value as _get_id_value

DEFAULT_LIMIT = 20

def do_get_one(db, doc_id, is_local):
    '''
    returns data of a single authorized info
    '''
    res = get_one(db, doc_id)
    if not res[0]:
        return res

    doc = res[1]
    if not is_local:
        try:
            for key in doc['spec']:
                if key.endswith('_secret') and doc['spec'][key]:
                    doc['spec'][key] = '****' + str(doc['spec'][key])[-4:]
        except:
            pass

    return (True, doc)

def do_get_list(db, is_local, offset=None, limit=None):
    '''
    returns data of a set of oauth infos
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]
    cursor = coll.find().sort([('_id', 1)])

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
        if not is_local:
            try:
                for key in entry['spec']:
                    if key.endswith('_secret') and entry['spec'][key]:
                        entry['spec'][key] = '****' + str(entry['spec'][key])[-4:]
            except:
                pass

        docs.append(entry)

    return (True, docs, {'total': total})

def do_delete_one(db, doc_id):
    '''
    deletes data of a single oauth info
    '''
    if not db:
        return (False, 'inner application error')

    doc_id = _get_id_value(doc_id)

    coll = db[collection]

    coll.remove({'_id': doc_id})

    return (True, {'_id': doc_id})

def do_post_one(db, auther_url, data):
    '''
    sets info of one app data and requests authorization initialization on it
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')
    spec_data = data['spec']

    for one_key in ['app_consumer_key', 'app_consumer_secret']:
        if (one_key not in spec_data) or (not spec_data[one_key]):
            return (False, str(one_key) + ' not provided')

    authini_data = {
        'oauth_info': {
            'consumer_key': spec_data['app_consumer_key'],
            'consumer_secret': spec_data['app_consumer_secret'],
        },
        'payload': {}
    }

    connector = controller.NewstwisterConnector(auther_url)
    res = connector.request_authini(authini_data['oauth_info'], authini_data['payload'])
    if not res[0]:
        err_msg = 'error during authini request dispatching: ' + res[1]
        return (False, err_msg)

    ret_envelope = res[1]
    if type(ret_envelope) is not dict:
        return (False, 'unknown form of returned authini data: ' + str(type(ret_envelope)))

    if ('status' not in ret_envelope) or (not ret_envelope['status']):
        err_msg = ''
        if ('error' in ret_envelope) and (ret_envelope['error']):
            err_msg = ': ' + str(ret_envelope['error'])
        return (False, 'status not acknowledged in returned authini data' + err_msg)
    if ('data' not in ret_envelope) or (not ret_envelope['data']):
        return (False, 'payload not provided in returned authini data')

    ret_data = ret_envelope['data']
    if type(ret_data) is not dict:
        return (False, 'unknown form of returned payload in authini data: ' + str(type(ret_data)))

    for part in ['oauth_token_key', 'oauth_token_secret', 'pin_url']:
        if (part not in ret_data) or (not ret_data[part]):
            return (False, 'returned authini data missing the "' + str(part) + '" part')

    try:
        if USE_SEQUENCES:
            entry = db['counters'].find_and_modify(query={'_id': collection}, update={'$inc': {'next':1}}, new=True, upsert=True, full_response=False)
            doc_id = entry['next']
        else:
            doc_id = ObjectId()
    except:
        return (False, 'can not create document id')

    timepoint = datetime.datetime.utcnow()
    created = timepoint
    updated = timepoint

    save_data = {
        '_id': doc_id,
        'spec': {
            'app_consumer_key': spec_data['app_consumer_key'],
            'app_consumer_secret': spec_data['app_consumer_secret'],
            'temporary_access_token_key': ret_data['oauth_token_key'],
            'temporary_access_token_secret': ret_data['oauth_token_secret'],
            'verifier_url': ret_data['pin_url'],
        },
        '_created': created,
        '_updated': updated,
    }

    coll = db[collection]

    doc_id = coll.save(save_data)
    if not doc_id:
        return (False, 'can not save the authini data')

    return (True, {'_id': doc_id})

def do_finalize_one(db, auther_url, doc_id, data):
    '''
    finalizes authorization initialization on info of one app data
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')
    spec = data['spec']

    coll = db[collection]

    if doc_id is None:
        return (False, 'document id not provided')

    doc_id = _get_id_value(doc_id)
    entry = coll.find_one({'_id': doc_id})
    if not entry:
        return (False, 'document of the provided _id not found')

    if ('spec' not in entry) or (type(entry['spec']) is not dict):
        return (False, 'damaged document structure')
    spec = entry['spec']

    needed_keys = ['app_consumer_key', 'app_consumer_secret', 'temporary_access_token_key', 'temporary_access_token_secret']
    for one_key in needed_keys:
        if (one_key not in spec) or (not spec[one_key]):
            return (False, 'document missing the "' + str(one_key) + '" part')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')
    spec_data = data['spec']

    for one_key in ['verifier_pin']:
        if (one_key not in spec_data) or (not spec_data[one_key]):
            return (False, str(one_key) + ' not provided')

    authfin_data = {
        'oauth_info': {
            'consumer_key': spec['app_consumer_key'],
            'consumer_secret': spec['app_consumer_secret'],
            'access_token_key': spec['temporary_access_token_key'],
            'access_token_secret': spec['temporary_access_token_secret'],
        },
        'payload': {
            'verifier': spec_data['verifier_pin'],
        }
    }

    connector = controller.NewstwisterConnector(auther_url)
    res = connector.request_authfin(authfin_data['oauth_info'], authfin_data['payload'])
    if not res[0]:
        err_msg = 'error during authfin request dispatching: ' + res[1]
        return (False, err_msg)

    ret_envelope = res[1]
    if type(ret_envelope) is not dict:
        return (False, 'unknown form of returned authfin data: ' + str(type(ret_envelope)))

    if ('status' not in ret_envelope) or (not ret_envelope['status']):
        err_msg = ''
        if ('error' in ret_envelope) and (ret_envelope['error']):
            err_msg = ': ' + str(ret_envelope['error'])
        return (False, 'status not acknowledged in returned authfin data' + err_msg)
    if ('data' not in ret_envelope) or (not ret_envelope['data']):
        return (False, 'payload not provided in returned authfin data')

    ret_data = ret_envelope['data']
    if type(ret_data) is not dict:
        return (False, 'unknown form of returned payload in authfin data: ' + str(type(ret_data)))

    for part in ['oauth_token_key', 'oauth_token_secret', 'user_id', 'screen_name']:
        if (part not in ret_data) or (not ret_data[part]):
            return (False, 'returned authfin data missing the "' + str(part) + '" part')

    try:
        screen_name_search = ret_data['screen_name'].lower()
    except:
        screen_name_search = ret_data['screen_name']

    timepoint = datetime.datetime.utcnow()
    created = timepoint
    updated = timepoint

    try:
        if ('_created' in entry) and entry['_created']:
            created = entry['_created']
    except:
        created = timepoint

    save_data = {
        '_id': doc_id,
        'spec': {
            'app_consumer_key': spec['app_consumer_key'],
            'app_consumer_secret': spec['app_consumer_secret'],
            'temporary_access_token_key': None,
            'temporary_access_token_secret': None,
            'authorized_access_token_key': ret_data['oauth_token_key'],
            'authorized_access_token_secret': ret_data['oauth_token_secret'],
            'verifier_url': None,
            'user_id': ret_data['user_id'],
            'screen_name': ret_data['screen_name'],
            'screen_name_search': screen_name_search,
        },
        '_created': created,
        '_updated': updated,
    }

    coll = db[collection]

    doc_id = coll.save(save_data)
    if not doc_id:
        return (False, 'can not save the authfin data')

    return (True, {'_id': doc_id})
