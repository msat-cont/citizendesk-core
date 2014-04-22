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

from citizendesk.feeds.twt.stream.storage import collection, schema
from citizendesk.common.utils import get_boolean as _get_boolean

DEFAULT_LIMIT = 30

'''
Request themselves are not stored in DB.
The found tweets are put in via Newstwister and Citizen Desk ingest.
Here we only return the status on the search.
'''

def _check_schema(spec, ctrl):
    '''
    TODO: move the thorough checking from Newstwister to here,
          and only keep simple key-value checking in the Newstwister itself.

    if spec:
        if ('oauth_id' in spec) and (spec['oauth_id'] is not None):
            if type(spec['oauth_id']) not in [int, long]:
                return (False, '"spec.oauth_id" has to be integer _id of oauth info')
        if ('filter_id' in spec) and (spec['filter_id'] is not None):
            if type(spec['filter_id']) not in [int, long]:
                return (False, '"spec.filter_id" has to be integer _id of filter info')

    if ctrl:
        if ('streamer_url' in ctrl) and (ctrl['streamer_url'] is not None):
            if type(ctrl['streamer_url']) not in [str, unicode]:
                return (False, '"control.streamer_url" has to be string')
        if ('switch_on' in ctrl) and (ctrl['switch_on'] is not None):
            if type(ctrl['switch_on']) not in [bool]:
                return (False, '"control.switch_on" has to be boolean')
    '''

    return (True,)

def do_post_search(db, user_id, request_id, search_spec):
    '''
    executes twitter search
    '''
    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    '''
    if data is None:
        return (False, 'data not provided')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')

    if doc_id is not None:
        if doc_id.isdigit():
            try:
                doc_id = int(doc_id)
            except:
                pass

    coll = db[collection]

    timepoint = datetime.datetime.utcnow()
    created = timepoint
    updated = timepoint
    started = None
    stopped = None

    entry = None
    if doc_id is not None:
        entry = coll.find_one({'_id': doc_id})
        if not entry:
            return (False, '"stream" of the provided _id not found')
        try:
            if ('logs' in entry) and (entry['logs']):
                if ('created' in entry['logs']) and entry['logs']['created']:
                    created = entry['logs']['created']
                if ('started' in entry['logs']) and entry['logs']['started']:
                    started = entry['logs']['started']
                if ('stopped' in entry['logs']) and entry['logs']['stopped']:
                    started = entry['logs']['stopped']
        except:
            created = timepoint
            started = None
            stopped = None

    doc = {
        'logs': {
            'created': created,
            'updated': updated,
            'started': started,
            'stopped': stopped
        },
        'spec': {},
        'control': {
            'streamer_url': None,
            'process_id': None,
            'switch_on': False
        }
    }

    for key in schema['spec']:
        doc['spec'][key] = None
        if key in data['spec']:
            doc['spec'][key] = data['spec'][key]

    res = _check_schema(doc['spec'], None)
    if not res[0]:
        return res

    # stop in any case, since filter/oauth specs might have changed
    might_run = True
    if not entry:
        might_run = False

    if might_run:
        if ('control' not in entry) or (type(entry['control']) is not dict):
            might_run = False

    if might_run:
        for key in schema['control']:
            if (key not in entry['control']) or (not entry['control'][key]):
                might_run = False
                break

    if might_run:
        connector = controller.NewstwisterConnector(entry['control']['streamer_url'])
        res = connector.request_stop(entry['control']['process_id'])
        if not res:
            return (False, 'can not stop the stream')
        # update info in db when we know it has been stopped
        timepoint = datetime.datetime.utcnow()
        doc['logs']['stopped'] = timepoint
        update_set = {'control.switch_on': False, 'control.process_id': None, 'logs.stopped': timepoint}
        coll.update({'_id': entry['_id']}, {'$set': update_set}, upsert=False)

    if not doc_id:
        try:
            entry = db['counters'].find_and_modify(query={'_id': collection}, update={'$inc': {'next':1}}, new=True, upsert=True, full_response=False);
            doc_id = entry['next']
        except:
            return (False, 'can not create document id')

    doc['_id'] = doc_id

    doc_id = coll.save(doc)

    return (True, {'_id': doc_id})
    '''

'''
def _prepare_filter(filter_spec):
    filter_use = {}
    if type(filter_spec) is not dict:
        return filter_use

    if ('language' in filter_spec) and filter_spec['language']:
        if type(filter_spec['language']) in [str, unicode]:
            filter_use['language'] = filter_spec['language']

    if ('locations' in filter_spec) and (type(filter_spec['locations']) is list):
        locations = []
        for item in filter_spec['locations']:
            if type(item) is not dict:
                continue
            can_use_item = True
            for item_key in ['west', 'east', 'north', 'south']:
                if item_key not in item:
                    can_use_item = False
                    break
                try:
                    str(item[item_key])
                except:
                    can_use_item = False
                    break
            if not can_use_item:
                continue
            item_location = ','.join([str(item[x]) for x in ['west', 'south', 'east', 'north']])
            locations.append(item_location)

        if locations:
            filter_use['locations'] = ','.join(locations)

    if ('track' in filter_spec) and (type(filter_spec['track']) is list):
        if filter_spec['track']:
            filter_use['track'] = ','.join([str(x) for x in filter_spec['track']])

    if ('follow' in filter_spec) and (type(filter_spec['follow']) is list):
        if filter_spec['follow']:
            filter_use['follow'] = ','.join([str(x) for x in filter_spec['follow']])

    return filter_use

def do_patch_one(db, doc_id=None, data=None, force=None):
    try:
        from citizendesk.feeds.twt.filter.storage import get_one as filter_get_one
    except:
        return (False, 'filter processor not available')
    try:
        from citizendesk.feeds.twt.oauth.storage import get_one as oauth_get_one
    except:
        return (False, 'oauth processor not available')

    if not controller:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')
    if type(data) is not dict:
        return (False, 'invalid data provided')

    if ('control' not in data) or (type(data['control']) is not dict):
        return (False, '"control" part not provided')

    if doc_id is None:
        return (False, 'stream _id not provided')

    if doc_id.isdigit():
        try:
            doc_id = int(doc_id)
        except:
            pass

    try:
        force_val = bool(_get_boolean(force))
    except:
        force_val = None

    coll = db[collection]

    entry = coll.find_one({'_id': doc_id})
    if not entry:
        return (False, '"stream" of the provided _id not found')
    if ('spec' not in entry) or (type(entry['spec']) is not dict):
        return (False, '"stream" of the provided _id does not contain "spec" part')

    doc = {'control': {}}
    for key in schema['control']:
        doc['control'][key] = None
        if key in data['control']:
            doc['control'][key] = data['control'][key]

    res = _check_schema(None, doc['control'])
    if not res[0]:
        return res

    should_run = False
    if doc['control']['switch_on']:
        if not doc['control']['streamer_url']:
            return (False, 'can not start the stream without the "streamer_url" being set')
        else:
            should_run = True

    filter_id = None
    oauth_id = None
    if should_run:
        if ('spec' in entry) and (type(entry['spec']) is dict):
            if 'filter_id' in entry['spec']:
                filter_id = entry['spec']['filter_id']
            if 'oauth_id' in entry['spec']:
                oauth_id = entry['spec']['oauth_id']

        if (not filter_id) or (not oauth_id):
            return (False, 'Can not start the stream without assigned filter_id and oauth_id')

    # load the supplemental data
    filter_info = None
    oauth_info = None
    if should_run:
        res = filter_get_one(db, filter_id)
        if not res[0]:
            return (False, 'filter info with _id equal to "spec.filter_id" not found')
        filter_info = res[1]
        if ('spec' not in filter_info) or (type(filter_info['spec']) is not dict):
            return (False, 'set filter without "spec" part')

        res = oauth_get_one(db, oauth_id)
        if not res[0]:
            return (False, 'oauth info with _id equal to "spec.oauth_id" not found')
        oauth_info = res[1]
        if ('spec' not in oauth_info) or (type(oauth_info['spec']) is not dict):
            return (False, 'set oauth without "spec" part')

    filter_spec = {}
    if filter_info and filter_info['spec']:
        try:
            filter_spec = _prepare_filter(filter_info['spec'])
        except:
            return (False, 'can not prepare filter params')

    # check if the oauth_id is not used by any other running feed
    if should_run:
        running_count = coll.find({'spec.oauth_id': oauth_id, 'control.switch_on': True, '_id': {'$ne': doc_id}}).count()
        if running_count:
            return (False, 'the "oauth_id" is already used at a running stream')

    # stop first in any case, since filter/oauth specs might have changed
    might_run = True
    if not entry:
        might_run = False

    if might_run:
        if ('control' not in entry) or (type(entry['control']) is not dict):
            might_run = False

    if might_run:
        for key in schema['control']:
            if (key not in entry['control']) or (not entry['control'][key]):
                might_run = False
                break

    if might_run:
        cur_stream_url = entry['control']['streamer_url']
        connector = controller.NewstwisterConnector(cur_stream_url)
        res = connector.request_stop(entry['control']['process_id'])
        if (not res) and (not force_val):
            return (False, 'can not stop the stream')
        # update info in db when we know it has been stopped
        timepoint = datetime.datetime.utcnow()
        update_set = {'control.switch_on': False, 'control.process_id': None, 'logs.stopped': timepoint}
        coll.update({'_id': doc_id}, {'$set': update_set}, upsert=False)

    if should_run:
        new_stream_url = doc['control']['streamer_url']
        connector = controller.NewstwisterConnector(new_stream_url)
        res = connector.request_start(str(doc_id), oauth_info['spec'], filter_spec)
        if not res:
            return (False, 'can not start the stream')
        try:
            proc_id = int(res)
        except:
            proc_id = res

        # update info in db when we know it has been started
        timepoint = datetime.datetime.utcnow()
        update_set = {'control.switch_on': True, 'control.process_id': proc_id, 'control.streamer_url': new_stream_url, 'logs.started': timepoint}
        coll.update({'_id': doc_id}, {'$set': update_set}, upsert=False)

    return (True, {'_id': doc_id})
'''

