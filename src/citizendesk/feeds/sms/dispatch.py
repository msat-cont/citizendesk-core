#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/sms/citizen/alias/
/feeds/sms/report/
/feeds/sms/send/
/feeds/sms/reply/

'''

def setup_blueprints(app):
    import citizendesk.feeds.sms.citizen_alias.connect as sms_citizen_alias_connect
    sms_citizen_alias_connect.setup_blueprints(app)

    import citizendesk.feeds.sms.report.connect as sms_report_connect
    sms_report_connect.setup_blueprints(app)

    import citizendesk.feeds.sms.send.connect as sms_send_connect
    sms_send_connect.setup_blueprints(app)

    import citizendesk.feeds.sms.reply.connect as sms_reply_connect
    sms_reply_connect.setup_blueprints(app)

    return
