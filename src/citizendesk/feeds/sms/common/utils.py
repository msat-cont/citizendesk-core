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
}

PHONE_NUMBER_ID_KEYS = ['user_id', 'user_name']
PHONE_NUMBER_SEARCH_KEYS = ['user_id_search', 'user_name_search']

MAXLEN_SHORTCODES = 6

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
    ''' return the first phone number available if any, used on sms-report authors and alike as well '''

    if (type(citizen_alias) is not dict) or (not citizen_alias):
        return None

    if ('authority' not in citizen_alias) or (citizen_alias['authority'] != get_conf('authority')):
        return None

    if ('identifiers' not in citizen_alias) or (type(citizen_alias['identifiers']) is not dict):
        return None

    for one_identifier_key in PHONE_NUMBER_ID_KEYS:
        if one_identifier_key not in citizen_alias['identifiers']:
            continue
        phone_number = citizen_alias['identifiers'][one_identifier_key]
        if not phone_number:
            continue
        try:
            phone_number = phone_number.strip()
        except:
            continue
        if not phone_number:
            continue
        return phone_number

    return None

def normalize_phone_number(phone_number):
    if not phone_number:
        return None

    try:
        phone_number = phone_number.strip().lstrip('+').lower()
        if len(phone_number) > MAXLEN_SHORTCODES:
            phone_number_stripped = phone_number.lstrip('0')
            if phone_number_stripped:
                phone_number = phone_number_stripped
    except:
        return None

    if not phone_number:
        return None

    return phone_number

def create_identities(phone_number):
    phone_number_normalized = normalize_phone_number(phone_number)

    identifiers = {}

    for identity_key in PHONE_NUMBER_ID_KEYS:
        identifiers[identity_key] = phone_number
    for identity_key in PHONE_NUMBER_SEARCH_KEYS:
        identifiers[identity_key] = phone_number_normalized

    return identifiers

