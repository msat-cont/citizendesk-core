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
from citizendesk.feeds.sms.common.reports import prepare_sms_send_report as _prepare_sms_send_report
from citizendesk.feeds.sms.send.storage import collection, schema
from citizendesk.common.utils import get_boolean as _get_boolean
from citizendesk.common.utils import get_id_value as _get_id_value

'''
Sending message to the specified recipients via an external SMS gateway
'''

def do_post_send(db, sms_gateway_url, sms_gateway_key, message, targets, user_id, language, sensitive, client_ip):
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
    if not targets:
        return (False, 'no targets provided')

    from citizendesk.feeds.sms.citizen_alias.storage import get_one_by_id as get_one_citizen_alias_by_id

    use_targets = []
    use_recipients = []
    use_phone_numbers = []

    authority = get_conf('authority')
    alias_doctype = get_conf('alias_doctype')

    if type(targets) not in [list, tuple]:
        return (False, '')
    for one_target in targets:
        if type(one_target) is not dict:
            continue
        if 'type' not in one_target:
            continue
        if one_target['type'] != alias_doctype:
            continue
        if 'value' not in one_target:
            continue

        one_target_id = _get_id_value(one_target['value'])
        alias_res = get_one_citizen_alias_by_id(db, one_target_id)
        if (not alias_res) or (not alias_res[0]):
            continue
        alias = alias_res[1]
        if (type(alias) is not dict) or (not alias):
            continue
        if ('identifiers' not in alias) or (not alias['identifiers']):
            continue

        one_phone_number = _get_phone_number(alias)
        if not one_phone_number:
            continue

        one_recipient = {'authority': authority, 'identifiers': alias['identifiers']}

        use_phone_numbers.append(one_phone_number)
        use_recipients.append(one_recipient)
        use_targets.append(one_target)

    if not use_targets:
        return (False, 'no valid recipient found')

    # putting all the recipients into a single report; and thus using its session for next communication with all the recipients
    try:
        report = _prepare_sms_send_report(use_targets, use_recipients, message, user_id, language, sensitive, client_ip)
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

