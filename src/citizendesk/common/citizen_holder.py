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
#user_id: Integer or None # if a local user is a creator of this alias info

#provider-based:
identifiers(user_name, user_id)
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

# logs
produced: DateTime # when the user info came (SMS sender) or was created (tweet user)
created: DateTime # document creation
modified: DateTime # last document modification

# flags
local: Boolean # if the alias was created by editors
sensitive: Boolean # whether it shall be kept secrete

Citizen structure:

_id: ObjectId() # just a unique identifier
aliases: List of aliases, as described above


nickname: String
identifiers: [{type:String, value:String, valid_from:Datetime, invalid_from:Datetime}]

# it is e.g.
{
    'nickname': 'citizen X',
    'identifiers':[
        {'phone_number':'123456789', valid_from:'2000-01-01', invalid_from:'2012-12-19'},
        {'twitter_id':'asdfghjkl', valid_from:'1970-01-01', invalid_from:None}
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

    def alias_present(self, authority, identifier):
        aliases = []

        coll = self.get_collection('aliases')

        alias_spec = {
            'authority': authority,
            'identifiers': identifier
        }

        cursor = coll.find(alias_spec).sort([('produced', 1)])
        for entry in cursor:
            aliases.append(entry)

        return aliases

    def save_alias(self, alias_info):
        alias = self.create_alias(alias_info)
        self.store_alias(alias)
        return True

    def store_alias(self, document):
        collection = self.get_collection('aliases')
        collection.save(document)

    def create_alias(self, alias_info):
        if type(alias_info) is not dict:
            return None

        for need_key in ['authority', 'identifiers']:
            if need_key not in alias_info:
                return None
            if not alias_info[need_key]:
                return None

        current_timestap = datetime.datetime.now()

        alias = {
            'change_id': 0, # TODO: get correct change id here!
            'authority': None,
            'identifiers': [],
            'avatars': [],
            'produced': None,
            'created': current_timestap,
            'name_first': None,
            'name_flast': None,
            'name_full': None,
            'locations': [],
            'time_zone': None,
            'languages': [],
            'description': None,
            'sources': [],
            'home_pages': [],
            'local': False,

            'notable': None,
            'reliable': None,
            'verified': False,
            'places': [],
            'comments': [],
            'links': [],
            'sensitive': None
        }

        parts_scalar = [
            'authority',
            'produced',
            'name_first',
            'name_flast',
            'name_full',
            'time_zone',
            'description',
            'local'
        ]

        parts_vector = [
            'identifiers',
            'avatars',
            'locations',
            'languages',
            'sources',
            'home_pages',
            'links'
        ]

        for key in parts_scalar:
            if key in alias_info:
                if alias_info[key]:
                    alias[key] = alias_info[key]

        for key in parts_vector:
            if key in alias_info:
                if type(alias_info[key]) not in [list, tuple]:
                    continue
                for one_value in alias_info[key]:
                    if one_value:
                        alias[key].append(one_value)

        if not alias['produced']:
            alias['produced'] = alias['created']

        return alias

    def update_alias(self, alias, alias_info):
        alias = self.adjust_alias(alias, alias_info)
        if not alias:
            return False

        print(alias)
        #try:
        if True:
            collection = self.get_collection('aliases')
            collection.update({'_id': alias['_id']}, alias, upsert=False)
        #except:
        #    return False

        return True

    def adjust_alias(self, alias, alias_info):
        parts_scalar = [
            'name_first',
            'name_flast',
            'name_full',
            'time_zone',
            'description',
        ]

        parts_vector = [
            'identifiers',
            'avatars',
            'locations',
            'languages',
            'sources',
            'home_pages'
        ]

        if type(alias) is not dict:
            return None

        if type(alias_info) is not dict:
            return None

        for key in parts_scalar:
            if (key in alias_info) and alias_info[key]:
                alias[key] = alias_info[key]

        for key in parts_vector:
            if (key in alias_info) and alias_info[key]:
                if type(alias_info[key]) not in [list, tuple]:
                    continue
                alias[key] = []
                for one_value in alias_info[key]:
                    if one_value:
                        alias[key].append(one_value)

        return alias

