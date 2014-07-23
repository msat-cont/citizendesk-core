#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/twt/filter/
/feeds/twt/oauth/
/feeds/twt/stream/
/feeds/twt/report/
/feeds/twt/endpoint/
/feeds/twt/session/
/feeds/twt/search/
/feeds/twt/citizen_alias/
/feeds/twt/authorized/
/feeds/twt/send/

'''

def setup_blueprints(app):
    import citizendesk.feeds.twt.filter.connect as twt_filter_connect
    twt_filter_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.oauth.connect as twt_oauth_connect
    twt_oauth_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.stream.connect as twt_stream_connect
    twt_stream_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.report.connect as twt_report_connect
    twt_report_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.search.connect as twt_search_connect
    twt_search_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.citizen_alias.connect as twt_citizen_alias_connect
    twt_citizen_alias_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.authorized.connect as twt_authorized_connect
    twt_authorized_connect.setup_blueprints(app)

    import citizendesk.feeds.twt.send.connect as twt_send_connect
    twt_send_connect.setup_blueprints(app)

    return
