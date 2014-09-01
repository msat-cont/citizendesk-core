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

try:
    long
except:
    long = int

from citizendesk.feeds.twt.search.storage import collection, schema
from citizendesk.common.utils import get_boolean as _get_boolean

DEFAULT_LIMIT = 30

'''
Request themselves are not stored in DB.
The found tweets are put in via Newstwister and Citizen Desk ingest.
Here we only return the status on the search.
'''

def _parse_data(search_spec):
    parsed = {}

    if type(search_spec) is not dict:
        return (False, 'unsupported search specification data')

    # having_any: boolean, true for OR, false for AND (default)
    # contains: keywords, #hashtags, @screen_names
    # since/until: yyyy-mm-dd
    # radius_unit: "km", "mi"
    # result_type: "mixed", "recent", "popular"
    #
    # search_spec = {
    #    'query': {'having_any': None, 'contains': [], 'from': None, 'to': None, 'without': None, 'since': None, 'until': None},
    #    'geocode': {'latitude': None, 'longitude': None, 'radius': None, 'radius_unit': None},
    #    'lang': None,
    #    'count': None,
    #    'since_id': None,
    #    'max_id': None,
    #    'result_type': None
    # }

    if ('query' not in search_spec) or (type(search_spec['query']) is not dict):
        return (False, 'query dictionary should be provided in "search_spec" data')
    query_part = search_spec['query']
    has_parts = False

    query_connective = ' '
    if ('having_any' in query_part) and query_part['having_any']:
        query_connective = ' OR '

    query_terms = []

    if ('contains' in query_part) and (type(query_part['contains']) in (list, tuple)) and query_part['contains']:
        for one_term in query_part['contains']:
            one_term = one_term.strip()
            if not one_term:
                continue
            if one_term.lower() in ['and', 'or']:
                return (False, 'boolean operators shall not be term parameters')
            if ' ' in one_term:
                if not one_term.startswith('"'):
                    one_term = '"' + one_term
                if not one_term.endswith('"'):
                    one_term = one_term + '"'
            query_terms.append(one_term)

    for spec_key in ['from', 'to']:
        if (spec_key in query_part) and query_part[spec_key]:
            screen_name = query_part[spec_key]
            if screen_name.startswith('@'):
                screen_name = screen_name[1:]
            if screen_name:
                query_terms.append(screen_name)

    if ('without' in query_part) and query_part['without']:
        query_terms.append('-' + query_part['without'])

    for spec_key in ['since', 'until']:
        if (spec_key in query_part) and query_part[spec_key]:
            date_str = query_part[spec_key]
            if not re.match('^[\d]{4}-[\d]{2}-[\d]{2}$', date_str):
                return (False, 'date specifiers shall be in the form "YYYY-MM-DD"')
            query_terms.append(spec_key + ':' + query_part[spec_key])

    parsed['q'] = query_connective.join(query_terms)
    if len(query_terms):
        has_parts = True

    if ('geocode' in search_spec) and (type(search_spec['geocode']) is dict):
        has_geo = True
        geo_part = search_spec['geocode']
        for geo_spec in ['latitude', 'longitude', 'radius', 'radius_unit']:
            if geo_spec not in geo_part:
                has_geo = False
                continue
            if not geo_part[geo_spec]:
                has_geo = False
                continue
        if has_geo:
            if geo_spec['radius_unit'] not in ['km', 'mi']:
                has_geo = False
                return (False, 'radius unit geo specifier shall be either "km" or "mi"')
        if has_geo:
            use_geocode = str(geo_part['latitude']) + ',' + str(geo_part['longitude']) + ','
            use_geocode += str(geo_part['radius']) + str(geo_part['radius_unit'])
            parsed['geocode'] = use_geocode
            has_parts = True

    for one_id_part in ['since_id', 'max_id']:
        if (one_id_part in search_spec) and search_spec[one_id_part]:
            if not str(search_spec[one_id_part]).isdigit():
                return (False, '"' + str(one_id_part) + '" shall be a digital string')
            parsed[one_id_part] = str(search_spec[one_id_part])
            has_parts = True

    if not has_parts:
        return (False, 'no applicable search specification provided')

    if ('count' in search_spec) and search_spec['count']:
        if not str(search_spec['count']).isdigit():
            return (False, '"count" shall be a digital string')
        parsed['count'] = str(search_spec['count'])

    if ('lang' in search_spec) and search_spec['lang']:
        if 2 is not len(search_spec['lang']):
            return (False, '"lang" shall be a (2-letter) language ISO 639-1 specification')
        parsed['lang'] = str(search_spec['lang'])

    parsed['result_type'] = 'mixed'
    if ('result_type' in search_spec) and search_spec['result_type']:
        if search_spec['result_type'] not in ['mixed', 'recent', 'popular']:
            return (False, '"result_type" shall be one of "mixed", "recent", "popular"')
        parsed['result_type'] = search_spec['result_type']

    return (True, parsed)

def do_post_search(db, searcher_url, user_id, request_id, search_spec):
    '''
    executes twitter search
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    for (part_name, part_value) in [['user_id', user_id], ['request_id', request_id], ['search_spec', search_spec]]:
        if not part_value:
            return (False, str(part_name) + ' not provided')

    if type(user_id) in [str, unicode]:
        if user_id.isdigit():
            try:
                user_id = int(user_id)
            except:
                pass

    if type(request_id) in [str, unicode]:
        if request_id.isdigit():
            try:
                request_id = int(request_id)
            except:
                pass

    try:
        parsed_res = _parse_data(search_spec)
        if not parsed_res[0]:
            return parsed_res
    except:
        return (False, 'could not parse the search specification data')

    '''
    coll = db[collection]

    timepoint = datetime.datetime.utcnow()
    created = timepoint
    updated = timepoint
    searched = None
    '''
    parsed_spec = parsed_res[1]

    connector = controller.NewstwisterConnector(searcher_url)
    res = connector.request_search(user_id, request_id, parsed_spec, search_spec)

    if not res:
        return (False, 'error during search request dispatching')

    return (True, res)

