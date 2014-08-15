#!/usr/bin/env python

import os, sys, datetime, json, logging
import urllib, urllib2

try:
    from srvcs_spec import services_info
except Exception as exc:
    print('the "srvcs_spec.py" file should contain specifications for remote services used on media')
    print(exc)
    sys.exit(1)

BASE_URL = 'http://localhost:9060'

def send_data():
    save_url = BASE_URL
    if not save_url.endswith('/'):
        save_url += '/'
    save_url += 'feeds/img/service/'

    for srvc_set in services_info:
        params = srvc_set

        save_status = None
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(save_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            save_result = response.read()
            save_status = json.loads(save_result)
        except Exception as exc:
            err_notice = ''
            try:
                err_notice = ', ' + exc.read()
            except:
                pass
            print('error during sending the services data: ' + str(exc) + err_notice)
            save_status = None

        print(save_status)

if __name__ == '__main__':
    send_data()

