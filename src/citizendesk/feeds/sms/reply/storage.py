#!/usr/bin/env python
#
# Citizen Desk
#

import datetime

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

collection = 'sms_sending'

schema = {
    'control': {
        'sms_gateway_url': 'url for communication with sms gateway',
        'sms_gateway_key': 'a password for sms-gateway communication'
    },
    'report_id': 'id of report: using authors from received sms, targets from sent sms',
    'message': 'the text to be sent as an sms',
    'user_id': 'citizendesk-user that sends the sms',
    'language': 'language used in sms; if provided',
    'sensitive': 'flag whether sms is sensitive; if provided'
}

