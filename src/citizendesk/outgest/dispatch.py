#!/usr/bin/env python
#
# Citizen Desk
#
'''
requests:
/streams/liveblog/
/streams/workingon/

config parts shall be named by directory names, urls should use that alike
'''

def setup_blueprints(app, config_data):
    import citizendesk.outgest.liveblog.connect as liveblog_connect
    config_part = None
    if type(config_data) is dict:
        if 'liveblog' in config_data:
            config_part = config_data['liveblog']
    liveblog_connect.setup_blueprints(app, config_part)

    import citizendesk.outgest.workingon.connect as workingon_connect
    config_part = None
    if type(config_data) is dict:
        if 'workingon' in config_data:
            config_part = config_data['workingon']
    workingon_connect.setup_blueprints(app, config_part)

    return
