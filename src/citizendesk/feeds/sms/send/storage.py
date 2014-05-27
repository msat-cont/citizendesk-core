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
        'secret': 'a password for sms-gateway communication'
    },
    'contacts': {
        'phone_numbers': ['+1234567890'],
        'local_groups': ['a_saved_group_of_citizens'],
        'gateway_groups': ['gateway-based_group_of_citizens']
    },
    'message': 'the text to be sent as an sms'
}


