#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
try:
    from citizendesk.external.feeds.twt import newstwisterc as control
except:
    control = None

try:
    unicode
except:
    unicode = str

#STATUS_IDLE = 0
#STATUS_WORK = 1

collection = 'twt_streams'

schema = {
    '_id': 1,
    'spec': {
        'oauth_id': '_id of oauth spec',
        'filter_id': '_id of filter spec',
        'desc': 'the purpose of this stream'
    },
    'control': {
        'streamer_url': 'http://localhost:9054/',
        'process_id': 'under which system id the stream runs',
        'works': 'controls whether stream is active'
    },
    'logs': {
        'created': '2014-03-12T12:00:00',
        'updated': '2014-03-12T12:00:00'
    }
}

'''
For this case, we have to check the status(es) on each GET request.
And for POST requests, we have to stop the stream first if it is active and anything changes.
Notice that a single oauth spec can only be used on a single stream.
'''

def do_get_one(db, doc_id):
    '''
    returns data of a single stream info
    '''
    if not control:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if doc_id is not None:
        if doc_id.isdigit():
            try:
                doc_id = int(doc_id)
            except:
                pass

    coll = db[collection]
    doc = coll.find_one({'_id': doc_id})

    if not doc:
        return (False, 'stream info not found')
    if ('spec' not in doc) or (type(doc['spec']) is not dict):
        return (False, 'wrong stream info (spec) in db')
    if ('control' not in doc) or (type(doc['control']) is not dict):
        return (False, 'wrong stream info (control) in db')

    might_run = True
    for key in schema['control']:
        if (key not in doc['control']) or (not doc['control'][key]):
            might_run = False
            break

    if might_run:
        connector = control.NewstwisterConnector(doc['control']['stream_url'])
        res = connector.request_status(doc['control']['process_id'])
        # let None here when can not check that it runs
        doc['control']['status'] = res
        if res is False:
            # update info in db when we know it does not run even though db says otherwise
            pass

    return (True, doc)

def do_get_list(db, offset=0, limit=20):
    '''
    returns data of a set of stream control
    '''
    if not control:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    coll = db[collection]
    cursor = coll.find()
    if offset:
        cursor = cursor.skip(offset)
    if limit:
        cursor = cursor.limit(limit)

    docs = []
    for entry in cursor:
        if not entry:
            continue
        if ('spec' not in entry) or (type(entry['spec']) is not dict):
            docs.append(entry)
            continue
        if ('stream_url' in entry['spec']) and entry['spec']['stream_url']:
            stream_url = entry['spec']['stream_url']
            connector = control.NewstwisterConnector(stream_url)
            res = connector.request_status(entry['_id'])
            if res is None:
                return (False, 'could not get stream status')
            entry['spec']['status'] = bool(res)

        docs.append(entry)

    return (True, docs)

def _check_schema(doc):

    for key in schema['spec']:
        if key not doc:
            return (False, '"' + str(key) + '" is missing in the data spec')
        if doc[key] is None:
            continue
        if type(doc[key]) not in [str, unicode]:
            return (False, '"' + str(key) + '" field has to be string')
    return True

def do_post_one(db, doc_id=None, data=None):
    '''
    sets data of a single stream info
    '''
    if not control:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    if data is None:
        return (False, 'data not provided')

    if ('spec' not in data) or (type(data['spec']) is not dict):
        return (False, '"spec" part not provided')
    spec = data['spec']

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

    entry = None
    if doc_id is not None:
        entry = coll.find_one({'_id': doc_id})
        if not entry:
            return (False, '"stream" of the provided _id not found')
        try:
            if ('logs' in entry) and (entry['logs']) and ('created' in entry['logs']):
                if entry['logs']['created']:
                    created = entry['logs']['created']
        except:
            created = timepoint

    doc = {
        'logs': {
            'created': created,
            'updated': updated
        },
        'spec': {}
    }

    for key in schema['spec']:
        doc['spec'][key] = None
        if key in spec:
            doc['spec'][key] = spec[key]

    res = _check_schema(doc['spec'])
    if not res[0]:
        return res

    # TODO: load the data
    oauth_spec = {}
    filter_spec = {}
    if doc['spec']['oauth_id'] and not oauth_spec:
        return (False, '"oauth_id" not found')
    if doc['spec']['filter_id'] and not filter_spec:
        return (False, '"filter_id" not found')

    # restart on any case when it should run, since filter/oauth specs might have changed
    differs = False
    if doc['spec']['status'] in [STATUS_WORK]:
        if oauth_spec and filter_spec:
            differs = True

    '''
    if (doc_id is not None) and entry and ('spec' in entry) and (type(entry['spec']) is dict):
        if ('status' in entry['spec']) and (entry['spec']['status'] in [STATUS_WORK]):
        entry['spec']
        for key in ['oauth_id', 'filter_id', 'stream_url', 'status']:
            if key not in entry['spec']:
                differs = True
                break
            if key not in doc['spec']:
                differs = True
                break
            if entry['spec'][key] != doc['spec'][key]:
                differs = True
                break
    '''

    if differs:
        connector = control.NewstwisterConnector(entry['spec']['stream_url'])
        res = connector.request_stop(doc_id)
        if (res is None) or res:
            return (False, 'can not stop the previously setup stream')

    if not doc_id:
        try:
            entry = db['counters'].find_and_modify(query={'_id': collection}, update={'$inc': {'next':1}}, new=True, upsert=True, full_response=False);
            doc_id = entry['next']
        except:
            return (False, 'can not create document id')

    doc['_id'] = doc_id

    doc_id = coll.save(doc)

    if ('stream_url' in doc['spec']) and doc['spec']['stream_url']:
        if ('status' in doc['spec']) and doc['spec']['status']:
            connector = control.NewstwisterConnector(doc['spec']['stream_url'])
            res = connector.request_start(doc_id, {'oauth_spec': oauth_spec, 'filter_spec': filter_spec})
            if not res:
                #coll.remove({'_id': doc_id})
                # TODO: set status to STATUS_IDLE
                if differs:
                    return (False, 'can not restart the stream')
                return (False, 'can not start the stream')

    return (True, {'_id': doc_id})

def do_delete_one(db, doc_id):
    '''
    deletes data of a single stream info
    '''
    if not control:
        return (False, 'external controller not available')
    if not db:
        return (False, 'inner application error')

    doc = do_get_one(db, doc_id)
    if not doc:
        return (False, 'requested stream not found')

    try:
        stream_url = doc['spec']['stream_url']
    except:
        stream_url = None
    if not stream_url:
        return (False, 'requested stream is not setup')

    #storage = control.NewstwisterStorage(db)
    connector = control.NewstwisterConnector(stream_url)

    #res = connector.request_stop(storage, doc_id)
    res = connector.request_stop(doc_id)
    if not res:
        return (False, 'could not stop the stream')

    coll = db[collection]

    coll.remove({'_id': doc_id})

    return (True, {'_id': doc_id})

