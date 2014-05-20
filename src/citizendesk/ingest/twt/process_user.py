#!/usr/bin/env python
#
# Citizen Desk
#
'''
If the user info is already saved, only update the provider-based parts.
'''

TWT_USER_LINK_PREFIX = 'https://twitter.com/'

import os, sys, datetime, json
from citizendesk.ingest.twt.connect import get_conf

def parse_user_info(authority, user_id, user_info, client_ip):

    if not user_id:
        return (False, 'alias id not provided')

    id_str = user_info.get('id_str')
    if user_id != id_str:
        return (False, 'alias ids differ')

    screen_name = user_info.get('screen_name')

    identifiers = []
    if id_str:
        identifiers.append({'type':'user_id', 'value':id_str})
    if screen_name:
        identifiers.append({'type':'user_name', 'value':screen_name})
        identifiers.append({'type':'user_name_lc', 'value':screen_name.lower()})
    if not identifiers:
        return (False, 'no alias identifiers provided')

    produced = user_info.get('created_at')
    #verified = user_info.get('verified')
    #if not verified:
    #    verified = False

    name_full = user_info.get('name')

    avatars = []
    image_http = user_info.get('profile_image_url')
    if not image_http:
        image_http = None
    image_https = user_info.get('profile_image_url_https')
    if not image_https:
        image_https = None
    if image_http or image_https:
        avatars.append({'http': image_http, 'https': image_https})

    locations = [user_info.get('location')] if user_info.get('location') else []
    time_zone = user_info.get('time_zone')

    languages = [user_info.get('lang')] if user_info.get('lang') else []
    description = user_info.get('description')

    home_pages = []
    if ('entities' in user_info) and (type(user_info['entities']) is dict):
        entities = user_info['entities']
        if ('url' in entities) and (type(entities['url']) is dict):
            url_entities = entities['url']
            if ('urls' in url_entities) and (type(url_entities['urls']) in [list, tuple]):
                for one_url in url_entities['urls']:
                    if type(one_url) is not dict:
                        continue
                    if 'expanded_url' not in one_url:
                        continue
                    one_link = one_url['expanded_url']
                    one_name = None
                    if ('display_url' in one_url) and one_url['display_url']:
                        one_name = one_url['display_url']
                    home_pages.append({'link': one_link, 'name': one_name})

    sources = [TWT_USER_LINK_PREFIX + str(screen_name)]

    alias = {
        'authority': authority,
        'identifiers': identifiers,
        'avatars': avatars,
        'produced': produced,
        'name_full': name_full,
        'locations': locations,
        'time_zone': time_zone,
        'languages': languages,
        'description': description,
        'sources': sources,
        'home_pages': home_pages
    }

    return (True, alias)

def do_post(holder, user_id, user_info, client_ip):

    authority = get_conf('authority')

    try:
        res = parse_user_info(authority, user_id, user_info, client_ip)
    except:
        return (False, 'error during parsing alias info')
    if not res[0]:
        return res

    alias = res[1]

    # check if the alias is already saved
    used_aliases = holder.alias_present(authority, {'type':'user_id', 'value':user_id})
    for one_alias in used_aliases:
        res = holder.update_alias(one_alias, alias)
        if not res:
            return (False, 'can not update citizen alias')
    if used_aliases:
        return (True, 'citizen alias updated')

    res = holder.save_alias(alias)
    if not res:
        return (False, 'can not save citizen alias')

    return (True, 'citizen alias saved')

