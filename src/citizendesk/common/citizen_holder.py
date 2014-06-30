#!/usr/bin/env python
#
# Citizen Desk
#
'''
Citizen alias structure:
# basic info
_id/alias_id: String # globally unique for any report from any feed
cId
authority: String # to know how to deal with it
created_by: Integer or None # if a local user is a creator of this alias info
updated_by: Integer or None # if a local user is a creator of this alias info
active: Bool # whether the citizen alias is used (or deactivated otherwise)

#provider-based:
identifiers(user_id, user_id_search, user_name, user_name_search)
#produced
avatars,
names (first name, last name, full name),
locations (town, country, any, time_zone),
time_zone
languages
description
sources
home_pages

#local-edited:
notable: Boolean
reliable: Boolean
verified: Boolean
places: List,
comments: List,
links: List,
tags: List,

#auto-generated on reports:
tags_auto: List

# logs
produced: DateTime # when the user info came (SMS sender) or was created (tweet user)
created: DateTime # document creation
modified: DateTime # last document modification

# flags
local: Boolean # if the alias was created by editors
sensitive: Boolean # whether it shall be kept secrete

# configuration
config: {'type':'value'} # for storing citizen_alias-related configuration

Citizen structure:

_id: ObjectId() # just a unique identifier
aliases: List of aliases, as described above


aliases: [{citizen_alias_id:ObjectId, valid_from:Datetime, invalid_from:Datetime}]

# it is e.g.
{
    'aliases':[
        {'citizen_alias_id': ObjectId(...), valid_from:'2000-01-01', invalid_from:'2012-12-19'},
        {'citizen_alias_id': ObjectId(...), valid_from:'1970-01-01', invalid_from:None}
    ]
}

'''

import os, sys, datetime
from citizendesk.common.dbc import mongo_dbs

COLL_ALIASES = 'citizen_aliases'
COLL_CITIZENS = 'citizens'
UNVERIFIED = 'unverified'
UPDATED_FIELD = 'modified'

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

    def get_const(self, name):
        known_names = {'unverified':UNVERIFIED}
        if name in known_names:
            return known_names[name]

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

        current_timestamp = datetime.datetime.now()

        alias = {
            #'change_id': 0, # TODO: get correct change id here!
            'authority': None,
            'active': True,
            'identifiers': {},
            'avatars': [],
            'produced': None,
            'created': current_timestamp,
            'name_first': None,
            'name_last': None,
            'name_full': None,
            'locations': [],
            'time_zone': None,
            'languages': [],
            'description': None,
            'sources': [],
            'home_pages': [],
            'local': False,
            'created_by': None,
            'updated_by': None,

            'notable': None,
            'reliable': None,
            'verified': False,
            'places': [],
            'comments': [],
            'links': [],
            'tags': [],
            'tags_auto': [],
            'sensitive': None,
            'config': {}
        }

        parts_scalar = [
            'authority',
            'active',
            'produced',
            'name_first',
            'name_last',
            'name_full',
            'time_zone',
            'description',
            'local',
            'created_by',
            'updated_by'
        ]

        parts_vector = [
            'avatars',
            'locations',
            'languages',
            'sources',
            'home_pages',
            'links',
            'tags',
            'tags_auto'
        ]

        parts_dict = [
            'identifiers',
            'config'
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
            alias['produced'] = alias['created']

        return alias

    def update_alias(self, alias, alias_info):
        alias = self.adjust_alias(alias, alias_info)
        if not alias:
            return False

        try:
            collection = self.get_collection('aliases')
            collection.update({'_id': alias['_id']}, alias, upsert=False)
        except:
            return False

        return True

    def adjust_alias(self, alias, alias_info):
        parts_scalar = [
            'name_first',
            'name_last',
            'name_full',
            'time_zone',
            'description',
            'updated_by'
        ]

        parts_vector = [
            'avatars',
            'locations',
            'languages',
            'sources',
            'home_pages'
        ]

        parts_dict = [
            'identifiers',
            'config'
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

