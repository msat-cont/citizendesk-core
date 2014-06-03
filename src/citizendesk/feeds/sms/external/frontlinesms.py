#!/usr/bin/env python

import os, sys, datetime, json, logging
import urllib, urllib2

class SMSConnector(object):
    ''' sending SMS to a SMS gateway '''

    def __init__(self, gateway_url, api_key):
        self.gateway_url = gateway_url
        self.api_key = api_key

    def send_sms(self, message, recipients):
        if not message:
            return (False, 'no message provided')

        if type(recipients) is not dict:
            return (False, 'wrong recipients specification')

        data = {
            'secret': str(self.api_key),
            'message': message,
            'recipients': []
        }

        some_recipients = False
        if ('phone_numbers' in recipients) and (type(recipients['phone_numbers']) in [list, tuple]):
            for phone_number in recipients['phone_numbers']:
                phone_number = phone_number.strip()
                if not phone_number:
                    continue
                data['recipients'].append({'type': 'address', 'value': phone_number})

        if not data['recipients']:
            return (False, 'no recipients provided')

        send_notice = None
        success = True
        try:
            post_data = json.dumps(data)
            req = urllib2.Request(self.gateway_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            send_notice = response.read()
            response.close()
        except Exception, exc:
            success = False

            err_notice = ''
            exc_other = ''
            try:
                exc_other += ' ' + str(exc.message).strip() + ','
            except:
                pass
            try:
                err_notice = str(exc.read()).strip()
                exc_other += ' ' + err_notice + ','
            except:
                pass
            if err_notice:
                send_notice = err_notice
            else:
                send_notice = str(exc) + str(exc_other)

        return (success, send_notice)

