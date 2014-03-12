#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/twt/filter/
/feeds/twt/oauth/
/feeds/twt/stream/
/feeds/twt/endpoint/

'''

def setup_blueprints(app):
    import citizendesk.feeds.twt.filter.connect as twt_filter_connect
    twt_filter_connect.setup_blueprints(app)

    return
