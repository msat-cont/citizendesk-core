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

from citizendesk.feeds.sms.common.utils import get_conf, gen_id
from citizendesk.feeds.sms.common.utils import extract_tags as _extract_tags
from citizendesk.feeds.sms.common.utils import get_phone_number_of_citizen_alias as _get_phone_number
from citizendesk.feeds.sms.common.utils import report_holder
from citizendesk.feeds.sms.common.reports import prepare_sms_reply_report as _prepare_sms_reply_report
from citizendesk.feeds.sms.send.storage import collection, schema
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_id_value as _get_id_value

'''
Sending message to sms-report targets/recipients via an external SMS gateway
'''

def do_post_reply(db, sms_gateway_url, sms_gateway_key, message, report_id, user_id, language, sensitive, client_ip):
    if not controller:
        return (False, 'no sms gateway controller available')
    if not db:
        return (False, 'no database available')

    if not sms_gateway_url:
        return (False, 'no sms gateway url configured')
    if not sms_gateway_key:
        return (False, 'no sms gateway key configured')

    if not message:
        return (False, 'no message provided')
    if not report_id:
        return (False, 'report_id not provided')

    from citizendesk.feeds.sms.report.storage import do_get_one_by_id as get_one_report_by_id
    from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_id as get_one_citizen_alias_by_id
    from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_phone_number as get_one_citizen_alias_by_phone_number

    report_id = _get_id_value(report_id)
    report_res = get_one_report_by_id(db, report_id)
    if not report_res[0]:
        return (False, 'report of given id not found')
    report_source = report_res[1]

    was_sent = False
    was_received = False

    channel_type = get_conf('channel_type')
    channel_value_send = get_conf('channel_value_send')
    channel_value_receive = get_conf('channel_value_receive')
    alias_doctype = get_conf('alias_doctype')
    authority = get_conf('authority')
    phone_identifier_type = get_conf('phone_identifier_type')

    if type(report_source) is not dict:
        return (False, 'wrong structure of report')
    if ('channels' in report_source) and (type(report_source['channels']) in (list, tuple)):
        for one_channel in report_source['channels']:
            if (type(one_channel) is dict) and ('type' in one_channel) and ('value' in one_channel):
                if one_channel['type'] != channel_type:
                    continue
                if one_channel['value'] == channel_value_send:
                    was_sent = True
                if one_channel['value'] == channel_value_receive:
                    was_received = True

    if (not was_sent) and (not was_received):
        return (False, 'unknown form of report')

    citizen_aliases = []

    if was_sent and ('targets' in report_source) and (type(report_source['targets']) in (list, tuple)):
        for one_target in report_source['targets']:
            if (type(one_target) is dict) and ('type' in one_target) and ('value' in one_target):
                if one_target['type'] == alias_doctype:
                    one_target_value = _get_id_value(one_target['value'])
                    one_citizen_alias_res = get_one_citizen_alias_by_id(db, one_target_value)
                    if one_citizen_alias_res[0]:
                        citizen_aliases.append(one_citizen_alias_res[1])

    if was_received and ('authors' in report_source) and (type(report_source['authors']) in (list, tuple)):
        for one_author in report_source['authors']:
            if (type(one_author) is dict) and ('authority' in one_author) and ('identifiers' in one_author):
                if one_author['authority'] != authority:
                    continue
                if type(one_author['identifiers']) not in (list, tuple):
                    continue
                for one_identity in one_author['identifiers']:
                    if type(one_identity) is not dict:
                        continue
                    if ('type' not in one_identity) or ('value' not in one_identity):
                        continue
                    if one_identity['type'] != phone_identifier_type:
                        continue
                    one_phone_number = one_identity['value']
                    one_citizen_alias_res = get_one_citizen_alias_by_phone_number(db, one_phone_number)
                    if one_citizen_alias_res[0]:
                        citizen_aliases.append(one_citizen_alias_res[1])

    if not citizen_aliases:
        return (False, 'not target suitable citizen alias found')

    use_targets = []
    use_recipients = []
    use_phone_numbers = []

    for one_citizen_alias in citizen_aliases:
        if (type(one_citizen_alias) is not dict):
            continue
        if ('_id' not in one_citizen_alias) or (not one_citizen_alias['_id']):
            continue
        one_target = {'type': alias_doctype, 'value': one_citizen_alias['_id']}

        if ('identifiers' not in one_citizen_alias) or (not one_citizen_alias['identifiers']):
            continue
        one_recipient = {'authority': authority, 'identifiers': one_citizen_alias['identifiers']}

        one_phone_number = _get_phone_number(one_citizen_alias)
        if not one_phone_number:
            continue

        use_phone_numbers.append(one_phone_number)
        use_recipients.append(one_recipient)
        use_targets.append(one_target)

    if not use_targets:
        return (False, 'no valid recipient found')

    # putting all the recipients into a single report; and thus using its session for next communication with all the recipients
    try:
        report = _prepare_sms_reply_report(report_source, use_targets, use_recipients, message, user_id, language, sensitive, client_ip)
    except:
        report = None
    if not report:
        return (False, 'report could not be prepared')

    # we either save the report before sms sending, and deleting it if sending fails,
    # or we first send sms, and if success on it, we save the report then;
    # thus either transiently having a false report, or a possibility of not having the report
    # on sent sms if the report saving fails at the end (should not hopefully though)

    doc_id = report_holder.save_report(report)
    if not doc_id:
        return (False, 'report could not be saved')

    connector = controller.SMSConnector(sms_gateway_url, sms_gateway_key)
    res = connector.send_sms(message, {'phone_numbers': use_phone_numbers})
    if not res[0]:
        report_holder.delete_report(doc_id)
        return (False, 'message could not be sent', res[1])

    return (True, {'_id': doc_id})

