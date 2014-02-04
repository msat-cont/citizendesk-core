#!/usr/bin/env python
#
# saving a report
#
'''

Report structure:

# basic info
_id/report_id: String # globally unique for any report from any feed
feed_type: String # to know how to deal with it
received: DateTime # when the report came
created: DateTime # document creation
modified: DateTime # last document modification

# status
verification: String # new, verified, false
importance: String # standard, urgent, ...
relevance: String # (ir)relevant, ...
checks: [{type:String, value:String, validator:String}]
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
identifiers: [{type:String, value:String}]

# it is e.g. {'identifiers':[{'phone_number':'123456789'}, {'twitter_id':'asdfghjkl'}]}

'''

import datetime

class ReportHolder(object):
    ''' dealing with reports regardless of their feed types '''
    def __init__(self):
        pass

    def get_collection(self):
        return None

    def get_conf(self, conf_name):
        return ''

    def gen_id(self, feed_type):
        return ''

    def get_const(self, name):
        return ''

    def store_report(self, document):
        collection = self.get_collection()
        collection.save(document)

    def create_report(self, data):

        feed_type = self.get_conf('feed_type')
        report_id = self.gen_id(feed_type)

        current_timestap = datetime.datetime.now()

        received = None
        if 'received' in data:
            importance = data['received']
        if not received:
            received = current_timestap

        unverified = self.get_const('UNVERIFIED')
        importance = None
        if 'importance' in data:
            importance = data['importance']

        document = {}
        # basic info
        document['_id'] = report_id
        document['feed_type'] = feed_type
        document['received'] = received
        document['created'] = current_timestap
        document['modified'] = current_timestap
        # status
        document['verification'] = unverified
        document['importance'] = importance
        document['relevance'] = None
        document['checks'] = [] # nothing here
        document['assignments'] = [] # nothing here
        # citizens
        document['channels'] = [] # should be filled
        document['publishers'] = [] # should be filled
        document['authors'] = [] # should be filled
        document['endorsers'] = [] # should be filled
        # content
        document['original'] = None # general data tree
        document['geolocations'] = [] # POIs from tweets, image exif data, city names, ...
        document['timeline'] = [] # recognized datetimes, image exif data, ...
        document['subjects'] = [] # recognized names
        document['media'] = [] # local binaries with refs
        document['texts'] = [] # selected text in bml, sent SMS, ...
        document['links'] = [] # link to bml site, ...
        document['transcripts'] = [] # nothing here
        document['notices'] = [] # nothing here
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

        self.insert_new_doc(document)

        # self.process_media()
        # self.process_texts()


    def provide_report(self, report_id):
        # output all report's data
        pass



