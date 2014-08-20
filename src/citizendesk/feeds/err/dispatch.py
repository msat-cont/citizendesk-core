#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/err/ingest/

'''

def setup_blueprints(app):
    import citizendesk.feeds.err.ingest.connect as err_ingest_connect
    err_ingest_connect.setup_blueprints(app)

    return
