#!/usr/bin/env python
#
# Citizen Desk
#

import datetime
try:
    from citizendesk.feeds.sms.external import frontlinesms as controller
except:
    controller = None

try:
    unicode
except:
    unicode = str

try:
    long
except:
    long = int

from citizendesk.feeds.sms.send.storage import collection, schema
from citizendesk.common.utils import get_boolean as _get_boolean

'''
Sending message to the specified recipients via an external SMS gateway
'''

def gen_id():
    return None

# this may should be put into a sms_utils.py file
def _extract_tags(message):
    return []

# this may should be put into a sms_utils.py file
def _extract_expand_links(message):
    return []

# TODO: these shall be two different methods/urls: "send" (with recipients), and "reply" with (parent_report)
def _prepare_sms_report(recipients, message, parent_message=None, user_id=None, language=None, sensitive=None, client_ip=None):
    ''' it may happen that the sms is a replay on something, we should cover it here '''

    channel = {
        'type': 'gateway', # i.e. not sent directly from a phone; take the string from a config
        'value':'sent', # 'received' for SMS we get; TODO: put this into sms ingest too!
        'filter':None,
        'reasons':None,
        'request':None
    }

    current_timestap = datetime.datetime.now()

    doc = {
        'report_id': gen_id(), # to generate the report_id
        'channels': [channel],
        'recipients': [], # by the provided recipients
        'authors': [], # no citizen here
        'endorsers': [], # no citizen here
        'publisher': 'sms_gateway', # from config
        'feed_type': 'SMS', # from config
        'parent_id': None, # if a reply
        'session': None, # by report_id, or if reply, take session_id of that parent/replied report
        'user_id': user_id, # who requested the sending, if not automatic
        'pinned_id': None, # if a reply, by the parent_message
        'coverage_id': None, # if a reply, by the parent_message
        'language': None, # if info provided
        'produced': current_timestap, # now, may be after sending
        'created': current_timestap, # now, may be after sending
        'assignments': [], # if a reply, by the parent_message
        'original': message,
        'texts': [{'original': message, 'transcript': None}],
        'tags': [], # we shall extract possible #tags, alike at sms receiving
        'links': [], # we shall extract possible (shortened) links; TODO: at sms receivng too!
        'is_published': False,
        'sensitive': False, # if info provided
        'summary': False,
        'local': True,
        'proto': False,
        'client_ip': client_ip # just as logging
    }

    # notice: we may need to parse the text for shortened links there, to expand them; for sms receiving as well

    for one_recipient in recipients:
        doc['recipients'].append({'authority': 'telco', 'identifiers': [{'type':'phone_number', 'value':one_recipient}]})

    if language:
        doc['language'] = language

    if sensitive is not None:
        doc['sensitive'] = sensitive

    if parent_message:
        doc['parent_id'] = parent_message['report_id']

    if parent_message:
        doc['session'] = parent_message['session']
    else:
        doc['session'] = doc['report_id']

    doc['tags'] = _extract_tags(message)

    doc['links'] = _extract_expand_links(message)

    if parent_message:
        if ('pinned_id' in parent_message) and parent_message['pinned_id']:
            doc['pinned_id'] = parent_message['pinned_id']
        if ('coverage_id' in parent_message) and parent_message['coverage_id']:
            doc['coverage_id'] = parent_message['coverage_id']

    return doc

def do_post_search(db, sms_gateway_url, sms_gateway_key, message, recipients):
    if not controller:
        return (False, '')
    if not db:
        return (False, '')

    if not sms_gateway_url:
        return (False, '')
    if not sms_gateway_key:
        return (False, '')

    if not message:
        return (False, '')
    if not recipients:
        return (False, '')

    if type(recipients) is not dict:
        return (False, '')
    if ('phone_numbers' not in recipients) or (type(recipients['phone_numbers']) not in [list, tuple]):
        return (False, '')

    '''
    reports = []
    for one_recipient in recipients['phone_numbers']:
        one_rep = _prepare_sms_report([one_recipient], message)
        reports.append(one_rep)
    '''
    # putting all the recipients into a single report; and thus using its session for next communication with all the recipients
    report = _prepare_sms_report(recipients['phone_numbers'], message)
    if not report:
        return (False, '')

    # we either save the report before sms sending, and deleting it if sending fails,
    # or we first send sms, and if success on it, we save the report then;
    # thus either transiently having a false report, or a possibility of not having the report
    # on sent sms if the report saving fails at the end (should not hopefully though)

    db.save_report(report)

    connector = controller.SMSConnector(sms_gateway_url, sms_gateway_key)
    res = connector.request_search(message, recipients)
    if not res:
        db.delete_report(report)
        return (False, '')
    if not res[0]:
        db.delete_report(report)
        return (False, '')

    return (True, report)

