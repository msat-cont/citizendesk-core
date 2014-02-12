#!/usr/bin/env python
#
# Citizen Desk
#
'''
Report structure:

# basic info
_id/report_id: String # globally unique for any report from any feed
feed_type: String # to know how to deal with it
feed_spec: String # can have several feeds of one type
produced: DateTime # when the report came (SMS) or was created (tweet)
created: DateTime # document creation
modified: DateTime # last document modification
session: String # grouping reports together
ptoto: Boolean # if the report has to be yet taken

# status
verification: String # new, verified, false
importance: String # standard, urgent, ...
relevance: String # (ir)relevant, ...
checks: [{type:String, status:String, validator:String}]
assignments: [{type:String, name:String}]

# citizens
channels: [{type:String, value:String}] # bookmarklet, sms, twitter, ...
publishers: [{type:String, value:String}] # youtube, flickr, ...
authors: [{type:String, value:String}] # who created the content
endorsers: [{type:String, value:String}] # who supports/submits/reports the content

# content
original: Any tree # original structured data
geolocations: [] # where it happened
timeline: [] # when the reported events happened
subjects: [] # who/what are the perpetrators
media: [] # local binaries with refs
texts: [] # original textual data
links: [] # links to referred sites
transcripts: [] # updated/adjusted texts, by staff journalists
notices: [{who:String, what:String}] # texts by staff journalists
comments: [{who:String, what:String}] # texts by (other) citizens
tags: [String] # (hash)tags. keywords, ...

# clients
viewed: [String] # nothing here
discarded: [String] # nothing here

Citizen structure:

_id: ObjectId() # just a unique identifier
nickname: String
identifiers: [{type:String, value:String, valid_from:Datetime, invalid_from:Datetime}]
session_quit: Boolean # to not continue this session, False ... this should be on a citizen (contact)

# it is e.g.
{
    'nickname': 'citizen X',
    'identifiers':[
        {'phone_number':'123456789', valid_from:'2000-01-01', invalid_from:'2012-12-19'},
        {'twitter_id':'asdfghjkl', valid_from:'1970-01-01', invalid_from:None}
    ]
}

Citizen settings:
type: String
spec: Dict
value: Dict

# it is e.g.
{
    {
        'type':'force_new_session',
        'spec': {'channel': {type:'SMS'}, 'author': {'type':'phone', 'value':'123456789'}},
        'value':{'set':True, 'once':True}
    }
}

'''

import os, sys, datetime
from citizendesk.reporting.dbc import mongo_dbs

COLL_REPORTS = 'reports'
COLL_CITIZENS = 'citizens'
UNVERIFIED = 'unverified'

class ReportHolder(object):
    ''' dealing with reports regardless of their feed types '''
    def __init__(self):
        self.db = None

    def get_collection(self, for_type):
        coll_names = {'reports':COLL_REPORTS, 'citizens':COLL_CITIZENS}
        if for_type in coll_names:
            return self.db[coll_names[for_type]]

        return None

    def gen_id(self, feed_type):

        rnd_list = [str(hex(i))[-1:] for i in range(16)]
        random.shuffle(rnd_list)
        id_value = '' + feed_type + ':'
        id_value += datetime.datetime.now().isoformat()
        id_value += ':' + ''.join(rnd_list)
        return id_value

    def get_const(self, name):
        known_names = {'unverified':UNVERIFIED}
        if name in known_names:
            return known_names[name]

        return None

    def store_report(self, document):
        collection = self.get_collection('reports')
        collection.save(document)

    def create_report(self, data):
        if not 'feed_type' in data:
            return None

        feed_type = data['feed_type']
        feed_spec = None
        if feed_spec in data:
            feed_spec = data['feed_spec']

        if 'report_id' in data:
            report_id = data['report_id']
        else:
            report_id = self.gen_id(feed_type)

        current_timestap = datetime.datetime.now()

        produced = None
        if 'produced' in data:
            importance = data['produced']
        if not produced:
            produced = current_timestap

        session = None
        if 'session' in data:
            importance = data['session']
        if not session:
            session = report_id

        unverified = self.get_const('unverified')
        importance = None
        if 'importance' in data:
            importance = data['importance']

        document = {}
        # basic info
        document['_id'] = report_id
        document['feed_type'] = feed_type
        document['feed_spec'] = feed_spec
        document['produced'] = produced
        document['created'] = current_timestap
        document['modified'] = current_timestap
        document['session'] = session
        document['proto'] = False
        # status
        document['verification'] = unverified
        document['importance'] = importance
        document['relevance'] = None
        document['checks'] = [] # nothing here; put here who did what checks!
        document['assignments'] = [] # nothing here
        # citizens
        document['channels'] = [] # should be filled
        document['publishers'] = [] # should be filled
        document['authors'] = [] # should be filled
        document['endorsers'] = [] # should be filled
        # content
        document['original'] = None # general data tree
        document['geolocations'] = [] # POIs from tweets, image exif data, city names, ...
        document['place_names'] = [] # free strings: town names, ...
        document['timeline'] = [] # recognized datetimes, image exif data, ...
        document['time_names'] = [] # recognized datetimes, image exif data, ...
        document['subjects'] = [] # recognized names
        document['media'] = [] # local binaries with refs, incl. metadata
        document['texts'] = [] # selected text in bml, sent SMS, ...
        document['links'] = [] # link to bml site, ...
        document['transcripts'] = [] # nothing here
        document['notices_inner'] = [] # nothing here
        document['notices_outer'] = [{'type':'before', 'value':'blah blah'}] # nothing here
        document['comments'] = [] # comment in bml
        document['tags'] = [] # (hash)tags
        # clients
        document['viewed'] = [] # nothing here
        document['discarded'] = [] # nothing here

        if 'original' in data:
            document['original'] = data['original']

        for part in ['channels', 'publishers', 'authors', 'endorsers']:
            value = []
            if part in data:
                value = data[part]
                if not value:
                    continue
                if type(value) is not list:
                    value = [value]
            document[part] = value

        for part in ['geolocations', 'texts', 'links', 'comments', 'tags']:
            value = []
            if part in data:
                value = data[part]
                if not value:
                    continue
                if type(value) is not list:
                    value = [value]
            document[part] = value

        media_data = []
        if 'media' in data:
            if data['media']:
                media_data = data['media']
                if type(media_data) is not list:
                    media_data = [media_data]

        for one_media in media_data:
            if type(one_media) is not dict:
                pass
            use_media = {'link': None, 'data': None, 'name': None}
            use_any = False
            for media_part in use_media:
                if media_part in one_media:
                    if one_media[media_part]:
                        use_media[media_part] = one_media[media_part]
                        use_any = True
            if use_any:
                document['media'].append(use_media)

    def save_report(self, data):
        report = self.create_report(data)
        self.store_report(report)

    def get_force_new_session(self, spec):

        force_new = False

        coll = self.get_collection('citizen_setting')
        spec_use = {'type':'force_new_session'}
        if 'channel' in spec:
            if 'type' in spec['channel']:
                spec_use['channel.type'] = spec['channel']['type']
            if 'value' in spec['channel']:
                spec_use['channel.type'] = spec['channel']['value']
        if 'author' in spec:
            if 'type' in spec['author']:
                spec_use['author.type'] = spec['author']['type']
            if 'value' in spec['channel']:
                spec_use['author.type'] = spec['author']['value']
        cursor = coll.find(spec_use, {'value': True, '_id':False})
        for entry in cursor:
            if ('value' in entry) and entry['value']:
                if ('set' in entry['value']) and entry['value']['set']:
                    force_new = True

        return force_new

    def clear_force_new_session(self, spec, once):
        coll = self.get_collection('citizen_setting')
        spec_use = {'type':'force_new_session'}
        if 'channel' in spec:
            if 'type' in spec['channel']:
                spec_use['channel.type'] = spec['channel']['type']
            if 'value' in spec['channel']:
                spec_use['channel.type'] = spec['channel']['value']
        if 'author' in spec:
            if 'type' in spec['author']:
                spec_use['author.type'] = spec['author']['type']
            if 'value' in spec['channel']:
                spec_use['author.type'] = spec['author']['value']
        if once:
            spec_use['value.once'] = True
        coll.remove(spec_use)


    def find_last_session(self, spec):
        coll = self.get_collection('reports')
        cursor = coll.find(spec, {'session':True, 'produced':True, '_id':False}).sort([('produced', -1)]).limit(1)
        if not cursor.count():
            return None
        report = cursor.next()
        return report

    def provide_report(self, report_id):
        # output all report's data
        coll = self.get_collection('reports')
        report = coll.find_one({'_id':report_id})
        if not report:
            return None
        report['report_id'] = report['_id']
        del(report['_id'])
        return report

    def provide_session(self, session_id):
        # output all reports of a session
        reports = []
        coll = self.get_collection('reports')
        cursor = coll.find({'session':session_id}).sort([('produced', 1)])
        for entry in cursor:
            entry['report_id'] = entry['_id']
            del(entry['_id'])
            reports.append(entry)
        return reports

    def list_feed_reports(self, feed_type, feed_spec=None, proto=False, offset=None, limit=None):
        # output (proto)reports of a feed
        reports = []
        coll = self.get_collection('reports')

        report_spec = {'feed_type':feed_type}
        if feed_spec is not None:
            report_spec['feed_spec'] = feed_spec
        report_spec['proto'] = proto

        cursor = coll.find(report_spec).sort([('produced', 1)])
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        for entry in cursor:
            entry['report_id'] = entry['_id']
            del(entry['_id'])
            reports.append(entry)

        return reports

    def list_channel_reports(self, channel_type, channel_value=None, proto=False, offset=None, limit=None):
        # output (proto)reports of a feed
        reports = []
        coll = self.get_collection('reports')

        if channel_value is None:
            report_spec = {'channels.type':channel_type}
        else:
            report_spec['channel'] = {'type':channel_type, 'value':channel_value}
        report_spec['proto'] = proto

        cursor = coll.find(report_spec).sort([('produced', 1)])
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        for entry in cursor:
            entry['report_id'] = entry['_id']
            del(entry['_id'])
            reports.append(entry)

        return reports

    def list_author_reports(self, author_type, author_value, proto=False, offset=None, limit=None):
        # output (proto)reports of a feed
        reports = []
        coll = self.get_collection('reports')

        report_spec['author'] = {'type':author_type, 'value':author_value}
        report_spec['proto'] = proto

        cursor = coll.find(report_spec).sort([('produced', 1)])
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        for entry in cursor:
            entry['report_id'] = entry['_id']
            del(entry['_id'])
            reports.append(entry)

        return reports

