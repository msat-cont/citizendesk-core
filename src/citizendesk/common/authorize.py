#!/usr/bin/env python
#
# Checking if the user is logged in, and if being allowed to deal with Citizen Desk
#

import urllib2, json
from flask import request, make_response
#from citizendesk.feeds.config import get_config

SESSION_FIELD_HEADER = 'Authorization'
SESSION_FIELD_PARAM = 'Authorization'
USER_ID_FIELD_HEADER = 'X-AuthorizeId'
USER_ID_FIELD_PARAM = 'AuthorizeId'

def get_config(key):
    config = {
        'authorization_url_template': 'http://sourcefabric.superdesk.pro/resources/my/HR/User/<user_id>/Role?X-Filter=Name',
        'user_id_replace_part': '<user_id>',
        'citizendesk_roles': ['Editor', 'Collaborator'],
    }
    if key not in config:
        return None
    return config[key]

def not_authorized():
    return make_response('Client not allowed\n\n', 403,)

def set_authorization(app_part):
    '''
    Putting the authorization checking for the required app or blueprint
    '''
    app_part.before_request(authorize_request)

def authorize_request():
    '''
    Making the authorization action itself
    '''
    allowed_roles = get_config('citizendesk_roles')

    session_value = request.headers.get(SESSION_FIELD_HEADER)
    if not session_value:
        session_value = request.args.get(SESSION_FIELD_PARAM)
    if not session_value:
        return not_authorized()

    user_id = request.headers.get(USER_ID_FIELD_HEADER)
    if not user_id:
        user_id = request.args.get(USER_ID_FIELD_PARAM)
    if not user_id:
        return not_authorized()

    check_url_template = get_config('authorization_url_template')
    replace_part = get_config('user_id_replace_part')
    check_url = check_url_template.replace(replace_part, str(user_id))
    try:
        check_request = urllib2.Request(check_url, headers={'Accept' : 'application/json', 'Content-Type': 'application/json'})
        check_response_data = urllib2.urlopen(check_request).read()
        role_list = json.loads(check_response_data)
    except:
        return not_authorized()

    if (not role_list) or (type(role_list) is not dict):
        return not_authorized()

    if ('RoleList' not in role_list) or (type(role_list['RoleList']) not in [list, tuple]):
        return not_authorized()

    for item in role_list['RoleList']:
        if type(item) is not dict:
            continue
        if 'Name' not in item:
            continue
        if item['Name'] in allowed_roles:
            return # no return value for allowing the request to pass on

    return not_authorized()

