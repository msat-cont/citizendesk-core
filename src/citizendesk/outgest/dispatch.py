#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/outgest/liveblog/


'''

def setup_blueprints(app):
    import citizendesk.outgest.liveblog.connect as liveblog_connect
    liveblog_connect.setup_blueprints(app)

    return
