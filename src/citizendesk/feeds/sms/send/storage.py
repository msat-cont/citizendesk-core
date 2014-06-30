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
    'targets': [
        {'type': 'citizen_alias', 'value': 'id_of_document_of_a_citizen_alias'}, # taking the first phone number, if found there
        #{'type': 'alias_group', 'value': 'id_of_document_of_an_alias_group'}, # taking the first phone number for each alias
    ],
    'message': 'the text to be sent as an sms',
    'user_id': 'citizendesk-user that sends the sms',
    'language': 'language used in sms; if provided',
    'sensitive': 'flag whether sms is sensitive; if provided'
}

