#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

FIELD_ACTIVE = 'active'
METHOD_CLIENT_GET = 'client_get'
SERVICE_IMAGE_TYPE = 'image'
URL_ENCODED_IMG_LINK = 'url_encoded_img_link'

collection = 'media_services'

schema = {
    '_id': 'ObjectId',
    'key': 'str',
    'title': 'str',
    'description': 'str',
    'notice': 'str',
    'site': 'str',
    'type': SERVICE_IMAGE_TYPE,
    'spec': {
        'method': METHOD_CLIENT_GET,
        'http': 'http://example.net/some/service/?img=<<img_link_url_encoded>>',
        'https': 'https://example.net/some/service/?img=<<img_link_url_encoded>>',
        'parameters': {
            '<<img_link_url_encoded>>': URL_ENCODED_IMG_LINK,
        },
    },
    FIELD_ACTIVE: 'bool',
}

def get_service_by_id(db, service_id):
    '''
    returns data of a single service
    '''
    if not db:
        return (False, 'inner application error')

    coll = db[collection]

    spec = {'_id': service_id}
    doc = coll.find_one(spec)

    if not doc:
        return (False, 'service not found')

    return (True, doc)

def update_service_set(db, service_id, update_set):
    '''
    updates data of a single service_id
    '''
    if not db:
        return (False, 'inner application error')

    check = get_service_by_id(db, service_id)
    if not check[0]:
        return (False, 'no such service')

    coll = db[collection]

    try:
        coll.update({'_id': service_id}, {'$set': update_set})
    except:
        return (False, 'can not make service update')

    return (True, {'_id': service_id})

