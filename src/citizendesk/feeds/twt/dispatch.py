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

    return
