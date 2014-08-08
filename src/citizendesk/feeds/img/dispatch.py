#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:

/feeds/img/service/

'''

def setup_blueprints(app):
    import citizendesk.feeds.img.service.connect as img_service_connect
    img_service_connect.setup_blueprints(app)

    return
