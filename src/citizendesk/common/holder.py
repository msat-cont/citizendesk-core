#!/usr/bin/env python
#
# Citizen Desk
#
'''
Report structure:

# basic info
_id: ObjectId # globally unique for any report from any feed
parent_id: String or None # e.g. reply_to id for tweet conversations
report_id: String # based on particular feeds, for linking, session_id, ...
session: String # grouping reports together
uuid: UUID4.hex # hex form of uuid4(), used for consumers to recognize the report on updates
client_ip: String # IP address of the coming report
user_id: ObjectId or None # if a local user is a creator of this report
pinned_id: ObjectId or None # id of a UI stream where the report is set
language: String or None # en, ...

#publishing
coverages: Dictionary
{
    outgested: List of ObjectIds of coverages that the report has/had been published in,
    published: List of ObjectIds of coverages that the report is published in,
    targeting: List of ObjectIds of coverages that the report is about/related to,
}
on_behalf_id : ObjectId or None # _id of local user that is set as a creator of the report

# logs
produced: DateTime # when the report came (SMS) or was created (tweet)
_created: DateTime # document creation
_updated: DateTime # last document modification
status_updated: DateTime # last change on (verification) status
_etag: String # for the purposes of Eve-related interfaces

# flags
proto: Boolean # if the report has to be yet taken
local: Boolean # if the report was created by editors
summary: Boolean
sensitive: Boolean # whether it is kind of "not at work" stuff
automatic: Boolean # if the report is created by an automated process, e.g. auto-reply
editable: Boolean # some report types (e.g. tweets) should not be edited
decayed: Boolean # if the report underwent decay

# status
assignments: [{user_id:String, type:String}]
steps: [{description:String, done:Boolean, validator:ObjectId}]
verified: Boolean # if the report has been verified; this is a temporary way
status: String # should hold name/_id of the verification status
importance: String # standard, urgent, ...
relevance: String # (ir)relevant, ...

# producers
feed_type: String # to know how to deal with it
publisher: String # youtube, flickr, ...
channels: [{type:String, value:String, filter, reasons(not reliable)}] # bookmarklet, sms, twitter (endpoints), ...

# citizens
authors: [{type:String, value:String}] # who created the content
recipients: [{type:String, value:String}] # who are targeted
endorsers: [{type:String, value:String}] # who supports/submits/reports the content
targets: [] # when local report, what are definitions of getting aliases

# content
original_id: String # if the original item has an id
original: Any tree # original structured data
geolocations: [] # where it happened
place_names: [] # free strings: town names, ...
timeline: [] # when the reported events happened
time_names: [] # recognized datetimes
citizens_mentioned: [{type:String, value:String}] # mentioned citizens, i.e. not (necessarily) the authors or recipients
subjects: [] # who/what are the perpetrators
media: [] # local binaries with refs
texts: [{'original': None, 'transcript': None}, ] # original and transcripted textual data
sources: [] # links of the report itself
links: [] # links to referred (external) sites
notices_inner: [{who:String, what:String}] # texts by staff journalists, for internal use
notices_outer: [{who:String, what:String}] # texts by staff journalists, for display
comments: [{who:String, what:String}] # texts by (other) citizens
tags: [String] # (hash)tags. keywords, ...

# regarding consumers: they should keep themselves the track of viewed and/or discarded reports

'''

import os, sys, datetime
import uuid
from citizendesk.common.dbc import mongo_dbs
from citizendesk.common.utils import get_etag as _get_etag

COLL_REPORTS = 'reports'
COLL_CITIZENS = 'citizens'
CREATED_FIELD = '_created'
UPDATED_FIELD = '_updated'

class ReportHolder(object):
    ''' dealing with reports regardless of their feed types '''
    def __init__(self):
        self.db = None

    def get_collection(self, for_type):
        self.db = mongo_dbs.get_db().db

        coll_names = {'reports':COLL_REPORTS, 'citizens':COLL_CITIZENS}
        if for_type in coll_names:
            use_coll_name = coll_names[for_type]
            return self.db[use_coll_name]

        return None

    def gen_id(self, feed_type):

        rnd_list = [str(hex(i))[-1:] for i in range(16)]
        random.shuffle(rnd_list)
        id_value = '' + feed_type + '||'
        id_value += datetime.datetime.utcnow().isoformat()
        id_value += '|' + ''.join(rnd_list)
        return id_value

    def store_report(self, document):
        try:
            collection = self.get_collection('reports')
            doc_id = collection.save(document)
        except:
            return False
        return doc_id

    def create_report(self, data):
        if not 'feed_type' in data:
            return None
        feed_type = data['feed_type']

        parent_id = None
        if 'parent_id' in data:
            parent_id = data['parent_id']

        if 'report_id' in data:
            report_id = data['report_id']
        else:
            report_id = self.gen_id(feed_type)

        session = None
        if 'session' in data:
            session = data['session']
        if not session:
            session = report_id

        client_ip = None
        if 'client_ip' in data:
            client_ip = data['client_ip']

        user_id = None
        if 'user_id' in data:
            user_id = data['user_id']

        pinned_id = None
        if 'pinned_id' in data:
            pinned_id = data['pinned_id']

        proto_report = False
        if 'proto' in data:
            proto_report = bool(data['proto'])

        local_report = False
        if 'local' in data:
            local_report = bool(data['local'])

        automatic_report = False
        if 'automatic' in data:
            automatic_report = bool(data['automatic'])

        editable_report = True
        if 'editable' in data:
            editable_report = bool(data['editable'])

        summary_report = False
        if 'summary' in data:
            summary_report = bool(data['summary'])

        sensitive_report = False
        if 'sensitive' in data:
            sensitive_report = bool(data['sensitive'])

        language = False
        if 'language' in data:
            language = data['language']

        current_timestamp = datetime.datetime.utcnow()

        produced = None
        if 'produced' in data:
            produced = data['produced']
        if not produced:
            produced = current_timestamp

        coverages = {'outgested': [], 'published': [], 'targeting': []}

        publisher = None
        if 'publisher' in data:
            publisher = data['publisher']

        importance = None
        if 'importance' in data:
            importance = data['importance']

        document = {}
        # basic info
        document['parent_id'] = parent_id
        document['report_id'] = report_id
        document['session'] = session
        document['uuid'] = str(uuid.uuid4().hex)
        document['client_ip'] = client_ip
        document['user_id'] = user_id
        document['pinned_id'] = pinned_id
        document['produced'] = produced
        document[CREATED_FIELD] = current_timestamp
        document[UPDATED_FIELD] = current_timestamp
        document['status_updated'] = current_timestamp
        #document['_etag'] = _get_etag()
        document['proto'] = proto_report
        document['local'] = local_report
        document['automatic'] = automatic_report
        document['editable'] = editable_report
        document['decayed'] = False
        document['summary'] = summary_report
        document['sensitive'] = sensitive_report
        document['language'] = language

        # publishing
        document['coverages'] = coverages
        #document['on_behalf_id'] = None

        # status
        document['assignments'] = [] # should be filled
        #document['steps'] = [] # nothing here; put here who did what checks!
        document['verified'] = False
        document['status'] = ''
        document['importance'] = importance
        document['relevance'] = None

        # producer
        document['feed_type'] = feed_type
        document['publisher'] = publisher
        document['channels'] = [] # should be filled

        # citizens
        document['authors'] = [] # should be filled
        document['recipients'] = [] # should be filled
        document['endorsers'] = [] # should be filled
        document['targets'] = [] # should be filled if local

        # content
        document['original_id'] = None
        if 'original_id' in data:
            document['original_id'] = data['original_id']
        document['original'] = None
        if 'original' in data:
            document['original'] = data['original']

        document['geolocations'] = [] # POIs from tweets, image exif data, city names, ...
        document['place_names'] = [] # free strings: town names, ...
        document['timeline'] = [] # recognized datetimes, image exif data, ...
        document['time_names'] = [] # recognized datetimes
        document['citizens_mentioned'] = [] # mentioned citizens
        document['subjects'] = [] # recognized names
        document['media'] = [] # local binaries with refs, incl. metadata
        document['texts'] = [] # [{'original': None, 'transcript': None}] selected text in bml, sent SMS, ...
        document['sources'] = [] # link to bml site, ...
        document['links'] = [] # link to referred sites, ...
        document['notices_inner'] = [] # nothing here
        document['notices_outer'] = [] # [{'type':destination, 'value':notice}]
        document['comments'] = [] # comment in bml
        document['tags'] = [] # (hash)tags

        list_keys = [
            'assignments', 'channels', 'authors', 'recipients', 'endorsers', 'targets',
            'geolocations', 'place_names', 'timeline', 'time_names', 'citizens_mentioned', 'subjects',
            'texts', 'sources', 'links', 'notices_inner', 'notices_outer', 'comments', 'tags',
        ]

        for part in list_keys:
            value = []
            if (part in data) and data[part]:
                value = data[part]
                if type(value) not in (list, tuple):
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
            use_media = {'link': None, 'link_ssl': None, 'data': None, 'name': None, 'width': None, 'height': None}
            use_any = False
            for media_part in use_media:
                if media_part in one_media:
                    if one_media[media_part]:
                        use_media[media_part] = one_media[media_part]
                        use_any = True
            if use_any:
                document['media'].append(use_media)

        return document

    def save_report(self, data):
        report = self.create_report(data)
        if not report:
            return False
        res = self.store_report(report)

        return res

    def delete_report(self, doc_id):
        try:
            collection = self.get_collection('reports')
            collection.remove({'_id': doc_id})
        except:
            return False
        return True

    def find_last_session(self, spec):
        coll = self.get_collection('reports')
        requested_fields = {
            'session': True,
            'produced': True,
            'pinned_id': True,
            'assignments': True,
            'report_id': True,
            '_id': True
        }

        cursor = coll.find(spec, requested_fields).sort([('produced', -1)]).limit(1)
        if not cursor.count():
            return None
        report = cursor.next()
        return report

    def provide_report(self, feed_type, report_id):
        # output all report's data
        coll = self.get_collection('reports')
        report = coll.find_one({'feed_type': feed_type, 'report_id':report_id})
        if not report:
            return None
        return report

    def provide_session(self, session_id):
        # output all reports of a session
        reports = []
        coll = self.get_collection('reports')
        cursor = coll.find({'session':session_id}).sort([('produced', 1)])
        for entry in cursor:
            reports.append(entry)
        return reports

    def list_feed_reports(self, feed_type, proto=None, offset=None, limit=None):
        # output (proto)reports of a feed
        reports = []
        coll = self.get_collection('reports')

        report_spec = {'feed_type':feed_type}
        if proto is not None:
            report_spec['proto'] = bool(proto)

        cursor = coll.find(report_spec).sort([('produced', 1)])
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        for entry in cursor:
            reports.append(entry)

        return reports

    def list_channel_reports(self, channel=None, proto=None, offset=None, limit=None):
        # output (proto)reports of a feed channel
        reports = []
        coll = self.get_collection('reports')

        report_spec = {'channel':channel}
        if proto is not None:
            report_spec['proto'] = bool(proto)

        cursor = coll.find(report_spec).sort([('produced', 1)])
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        for entry in cursor:
            reports.append(entry)

        return reports

    def list_channel_spec_reports(self, channel_type, channel_value=None, proto=None, offset=None, limit=None):
        # output (proto)reports of a feed
        reports = []
        coll = self.get_collection('reports')

        if channel_value is None:
            report_spec = {'channels.type':channel_type}
        else:
            report_spec['channel'] = {'type':channel_type, 'value':channel_value}
        if proto is not None:
            report_spec['proto'] = bool(proto)

        cursor = coll.find(report_spec).sort([('produced', 1)])
        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        for entry in cursor:
            reports.append(entry)

        return reports

    def add_channels(self, feed_type, report_id, channels):
        if (not report_id) or (not channels) or (type(channels) is not list):
            return
        coll = self.get_collection('reports')

        timepoint = datetime.datetime.utcnow()
        log_parts = {
            UPDATED_FIELD: timepoint,
            #'_etag': _get_etag(),
        }
        coll.update({'feed_type': feed_type, 'report_id': report_id}, {'$addToSet': {'channels': {'$each': channels}}, '$set': log_parts}, upsert=False)

    def add_endorsers(self, feed_type, report_id, endorsers):
        if (not report_id) or (not endorsers) or (type(endorsers) is not list):
            return
        coll = self.get_collection('reports')

        timepoint = datetime.datetime.utcnow()
        log_parts = {
            UPDATED_FIELD: timepoint,
            #'_etag': _get_etag(),
        }
        coll.update({'feed_type': feed_type, 'report_id': report_id}, {'$addToSet': {'endorsers': {'$each': endorsers}}, '$set': log_parts}, upsert=False)

