#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/any/report/
/feeds/any/coverage/

'''

def setup_blueprints(app):
    import citizendesk.feeds.any.report.connect as any_report_connect
    any_report_connect.setup_blueprints(app)

    import citizendesk.feeds.any.coverage.connect as any_coverage_connect
    any_coverage_connect.setup_blueprints(app)

    return
