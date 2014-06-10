#!/usr/bin/env python

import os, sys, datetime, json, logging, random
import urllib, urllib2

from citizendesk.common.holder import ReportHolder
report_holder = ReportHolder()

from citizendesk.common.citizen_holder import CitizenHolder
citizen_holder = CitizenHolder()

config = {
    'feed_type': 'sms',
    'publisher': 'sms_gateway', # i.e. not sent directly from a phone
    'channel_type': 'sms', # whether sms, mms, ...
    'channel_value_send': 'sent', # 'sent' for sending (incl. replying)
    'channel_value_receive': 'received', # 'received' for SMS we get; use this in sms ingest too!
    'authority': 'telco',
    'alias_doctype': 'citizen_alias',
    'phone_identifier_type': 'phone_number'
}

def set_conf(name, value):
    global config

    config[name] = value

def get_conf(name):
    global config

    if name in config:
        return config[name]
    return None

def gen_id(feed_type, channel_type, channel_value, timestamp):
    rnd_list = [str(hex(i))[-1:] for i in range(16)]
    random.shuffle(rnd_list)

    report_id = feed_type + '//' + channel_type + '/' + channel_value + '/'
    report_id += timestamp.isoformat() + '/'
    report_id += ''.join(rnd_list)

    return report_id

def extract_tags(message):
    tags = []
    if message:
        try:
            for word in message.split(' '):
                word = word.strip()
                if word.startswith('#'):
                    use_tag = word[1:]
                    if use_tag:
                        tags.append(use_tag)
        except:
            return []

    return tags

def get_phone_number_of_citizen_alias(citizen_alias):
    ''' return the first phone number available if any '''

    phone_identifier_type = get_conf('phone_identifier_type')

    if (type(citizen_alias) is not dict) or (not citizen_alias):
        return None

    if ('identifiers' not in citizen_alias) or (type(citizen_alias['identifiers']) not in [list, tuple]):
        return None

    for one_identifier in citizen_alias['identifiers']:
        if type(one_identifier) is not dict:
            continue
        if ('type' not in one_identifier) or ('value' not in one_identifier):
            continue
        if one_identifier['type'] != phone_identifier_type:
            continue
        try:
            phone_number = one_identifier['value'].strip()
        except:
            continue
        if not phone_number:
            continue
        return phone_number

    return None

