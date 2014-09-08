#!/usr/bin/env python
#
# Citizen Desk
#
'''
Citizen alias structure:
# basic info
_id: ObjectId # globally unique for any report from any feed
uuid: UUID4.hex # hex form of uuid4(), used for consumers to recognize the author on updates
active: Bool # whether the citizen alias is used (or deactivated otherwise)

#provider-based identification:
authority: String # to know how to deal with it
identifiers(user_id, user_id_search, user_name, user_name_search)

#provider-based names:
name_first: String or None
name_last: String or None
name_full: String or None

#provider-based other properties:
avatars: [{'http': URL, 'https': URL}]
locations: [String] # (town, country, any, time_zone)
time_zone: String
languages: [String]
description: String
sources: [URL]
home_pages: [{link: URL, name: String}]

#local-edited:
notable: Boolean or None
reliable: Boolean or None
verified: Boolean
places: List,
comments: List,
links: List,
tags: List,

#auto-generated on reports:
tags_auto: List

# logs
produced: DateTime # when the user info came (SMS sender) or was created (tweet user)
_created: DateTime # document creation
_updated: DateTime # last document modification
created_by: ObjectId # user that created the citizen alias, if locally created
updated_by: ObjectId # user that updated the citizen alias, if locally updated

# flags
local: Boolean # if the alias was created by editors
sensitive: Boolean # whether it shall be kept secrete

# configuration
config: {'type':'value'} # for storing citizen_alias-related configuration


Citizen structure:
_id: ObjectId # just a unique identifier
aliases: {alias_id: ObjectId, preferred: Boolean} # links to ObjctIds of citizen aliases
'''

import os, sys, datetime
import uuid
from citizendesk.common.dbc import mongo_dbs
from citizendesk.common.utils import get_etag as _get_etag

COLL_ALIASES = 'citizen_aliases'
COLL_CITIZENS = 'citizens'
CREATED_FIELD = '_created'
UPDATED_FIELD = '_updated'

class CitizenHolder(object):
    ''' dealing with citizens regardless of their authority types '''
    def __init__(self):
        self.db = None

    def get_collection(self, for_type):
        self.db = mongo_dbs.get_db().db

        coll_names = {'aliases':COLL_ALIASES, 'citizens':COLL_CITIZENS}
        if for_type in coll_names:
            use_coll_name = coll_names[for_type]
            return self.db[use_coll_name]

        return None

    def alias_present(self, authority, identifier_type, identifier_value):
        aliases = []

        coll = self.get_collection('aliases')

        identifier_key = 'identifiers.' + str(identifier_type)
        alias_spec = {
            'authority': authority,
            identifier_key: identifier_value
        }

        cursor = coll.find(alias_spec).sort([('produced', 1)])
        for entry in cursor:
            aliases.append(entry)

        return aliases

    def save_alias(self, alias_info):
        alias = self.create_alias(alias_info)
        res = self.store_alias(alias)
        return res

    def store_alias(self, document):
        collection = self.get_collection('aliases')
        try:
            alias_id = collection.save(document)
        except:
            return None
        return alias_id

    def create_alias(self, alias_info):
        if type(alias_info) is not dict:
            return None

        for need_key in ['authority', 'identifiers']:
            if need_key not in alias_info:
                return None
            if not alias_info[need_key]:
                return None

        current_timestamp = datetime.datetime.utcnow()

        alias = {
            'uuid': str(uuid.uuid4().hex),
            'active': True,
            'authority': None,
            'identifiers': {},
            'produced': None,
            CREATED_FIELD: current_timestamp,
            UPDATED_FIELD: current_timestamp,
            #'_etag': _get_etag(),
            'local': False,
            'sensitive': None,
            'created_by': None,
            'updated_by': None,

            'name_first': None,
            'name_last': None,
            'name_full': None,
            'avatars': [],
            'locations': [],
            'time_zone': None,
            'languages': [],
            'description': None,
            'sources': [],
            'home_pages': [],

            'notable': None,
            'reliable': None,
            'verified': False,
            'places': [],
            'comments': [],
            'links': [],
            'tags': [],
            'tags_auto': [],

            'config': {},
        }

        parts_scalar = [
            'authority',
            'active',
            'produced',
            'local',
            'sensitive',
            'created_by',
            'updated_by',
            'name_first',
            'name_last',
            'name_full',
            'time_zone',
            'description',
            'notable',
            'reliable',
            'verified',
        ]

        parts_vector = [
            'avatars',
            'locations',
            'languages',
            'sources',
            'home_pages',
            'places',
            'comments',
            'links',
            'tags',
            'tags_auto',
        ]

        parts_dict = [
            'identifiers',
            'config',
        ]

        for key in parts_scalar:
            if key in alias_info:
                if alias_info[key] is not None:
                    alias[key] = alias_info[key]

        for key in parts_vector:
            if key in alias_info:
                if type(alias_info[key]) not in [list, tuple]:
                    continue
                for one_value in alias_info[key]:
                    if one_value is not None:
                        alias[key].append(one_value)

        for key in parts_dict:
            if key in alias_info:
                if type(alias_info[key]) is not dict:
                    continue
                for one_key in alias_info[key]:
                    if alias_info[key][one_key] is not None:
                        alias[key][one_key] = alias_info[key][one_key]

        if not alias['produced']:
            alias['produced'] = alias[CREATED_FIELD]

        return alias

    def update_alias(self, alias, alias_info):
        alias_set = self.adjust_alias({}, alias_info)
        if not alias_set:
            return False

        alias_set[UPDATED_FIELD] = datetime.datetime.utcnow()
        #alias_set['_etag'] = _get_etag()

        try:
            collection = self.get_collection('aliases')
            collection.update({'_id': alias['_id']}, {'$set': alias_set}, upsert=False)
        except:
            return False

        return True

    def adjust_alias(self, alias, alias_info):
        parts_scalar = [
            'active',
            'sensitive',
            'updated_by',
            'name_first',
            'name_last',
            'name_full',
            'time_zone',
            'description',
            'notable',
            'reliable',
            'verified',
        ]

        parts_vector = [
            'avatars',
            'locations',
            'languages',
            'sources',
            'home_pages',
            'places',
            'comments',
            'links',
            'tags',
            'tags_auto',
        ]

        parts_dict = [
            'identifiers',
            'config',
        ]

        if type(alias) is not dict:
            return None

        if type(alias_info) is not dict:
            return None

        for key in parts_scalar:
            if (key in alias_info) and (alias_info[key] is not None):
                alias[key] = alias_info[key]

        for key in parts_vector:
            if (key in alias_info):
                if type(alias_info[key]) not in [list, tuple]:
                    continue
                alias[key] = []
                for one_value in alias_info[key]:
                    if one_value is not None:
                        alias[key].append(one_value)

        for key in parts_dict:
            if key in alias_info:
                if type(alias_info[key]) is not dict:
                    continue
                alias[key] = {}
                for one_key in alias_info[key]:
                    if alias_info[key][one_key] is not None:
                        alias[key][one_key] = alias_info[key][one_key]

        return alias

