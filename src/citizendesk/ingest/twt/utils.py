#!/usr/bin/env python
#
# Citizen Desk
#

from citizendesk.common.holder import ReportHolder

holder = ReportHolder()

def get_conf(name):
    config = {
        'feed_type': 'tweet',
        'publisher': 'twitter',
        'authority': 'twitter'
    }

    if name in config:
        return config[name]
    return None

def gen_id(feed_type, id_str):
    try:
        id_value = '' + feed_type + '||' + id_str
        return id_value
    except:
        return None

def get_tweet(report_id):
    try:
        return holder.provide_report(get_conf('feed_type'), report_id)
    except:
        return None

