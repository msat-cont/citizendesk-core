#!/usr/bin/env python

import os, sys, datetime, json, logging, random
import urllib, urllib2

from citizendesk.common.holder import ReportHolder
report_holder = ReportHolder()

from citizendesk.common.citizen_holder import CitizenHolder
citizen_holder = CitizenHolder()

config = {
    'feed_type': 'SMS',
    'publisher': 'sms_gateway',
    'channel_type': 'gateway', # i.e. not sent directly from a phone
    'channel_value_send': 'sent', # 'sent' for sending
    'channel_value_reply': 'replied', # 'replied' for replying
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

def gen_id(channel_type, channel_value, targets, timestamp):
    rnd_list = [str(hex(i))[-1:] for i in range(16)]
    random.shuffle(rnd_list)

    report_id = get_conf('feed_type') + ':' + channel_type + ':' + channel_value + ':'
    report_id += timestamp.isoformat() + ':'
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

