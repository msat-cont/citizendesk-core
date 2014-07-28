#!/usr/bin/env python

import os, sys, datetime, json, logging
import urllib, urllib2
import copy

class NewstwisterConnector():
    def __init__(self, base_url):
        self.ctrl_base_url = base_url

    def request_authini(self, authini_oauth, authini_payload):
        auth_url = self.ctrl_base_url
        if not auth_url.endswith('/'):
            auth_url += '/'
        auth_url += '_authini'

        params = {}
        params['oauth_info'] = authini_oauth
        params['payload'] = authini_payload

        auth_status = None
        success = True
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(auth_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            auth_result = response.read()
            auth_status = json.loads(auth_result)
        except Exception as exc:
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
                auth_status = err_notice
            else:
                auth_status = str(exc) + str(exc_other)

        return (success, auth_status)

    def request_authfin(self, authfin_oauth, authfin_payload):
        auth_url = self.ctrl_base_url
        if not auth_url.endswith('/'):
            auth_url += '/'
        auth_url += '_authfin'

        params = {}
        params['oauth_info'] = authfin_oauth
        params['payload'] = authfin_payload

        auth_status = None
        success = True
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(auth_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            auth_result = response.read()
            auth_status = json.loads(auth_result)
        except Exception as exc:
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
                auth_status = err_notice
            else:
                auth_status = str(exc) + str(exc_other)

        return (success, auth_status)

    def send_tweet(self, authorized_data, tweet_data):
        send_url = self.ctrl_base_url
        if not send_url.endswith('/'):
            send_url += '/'
        send_url += '_tweet'

        params = {}
        params['oauth_info'] = authorized_data
        params['payload'] = tweet_data

        send_status = None
        success = True
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(send_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            send_result = response.read()
            send_status = json.loads(send_result)
        except Exception as exc:
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
                send_status = err_notice
            else:
                send_status = str(exc) + str(exc_other)

        return (success, send_status)

    def request_user(self, search_spec):
        search_url = self.ctrl_base_url
        if not search_url.endswith('/'):
            search_url += '/'
        search_url += '_user'

        params = {}
        params['type'] = 'user_info'
        params['params'] = search_spec

        search_status = None
        success = True
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(search_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            search_result = response.read()
            search_status = json.loads(search_result)
        except Exception as exc:
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
                search_status = err_notice
            else:
                search_status = str(exc) + str(exc_other)

        return (success, search_status)

    def request_search(self, user_id, request_id, search_spec, search_original):
        search_url = self.ctrl_base_url
        if not search_url.endswith('/'):
            search_url += '/'
        search_url += '_search'

        params = {}
        params['user_id'] = user_id
        params['request_id'] = request_id
        params['search_spec'] = search_spec
        params['search_spec_original'] = search_original

        search_status = None
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(search_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            search_result = response.read()
            search_status = json.loads(search_result)
            if type(search_status) is not dict:
                search_status = None
        except Exception as exc:
            search_status = None

        return search_status

    def request_start(self, endpoint_id, oauth_params, filter_params, filter_original):
        # make connection to twister_main
        # take response from connection

        start_url = self.ctrl_base_url
        if not start_url.endswith('/'):
            start_url += '/'
        start_url += '_start'

        params = {}
        params['oauth_info'] = oauth_params
        params['stream_filter'] = filter_params
        params['stream_spec_original'] = filter_original
        params['endpoint'] = {'endpoint_id': endpoint_id}

        node_status = None
        try:
            post_data = json.dumps(params)
            req = urllib2.Request(start_url, post_data, {'Content-Type': 'application/json'})
            response = urllib2.urlopen(req)
            node_result = response.read()
            node_status = json.loads(node_result)
            if type(node_status) is not dict:
                node_status = None
        except Exception as exc:
            #print(exc.read())
            node_status = None

        if node_status is None:
            return None

        if 'node' not in node_status:
            return None
        if 'status' not in node_status:
            return None

        if not node_status['node']:
            return False
        if not node_status['status']:
            return False

        return node_status['node']

    def request_stop(self, node_id):
        stop_url = self.ctrl_base_url
        if not stop_url.endswith('/'):
            statop_url += '/'
        stop_url += '_stop'

        params = {}
        params['node'] = str(node_id)

        node_status = None
        try:
            for param_key in params:
                params[param_key] = params[param_key].encode('utf8')

            post_data = urllib.urlencode(params)
            req = urllib2.Request(stop_url, post_data)
            response = urllib2.urlopen(req)
            node_result = response.read()
            node_status = json.loads(node_result)
            if type(node_status) is not dict:
                node_status = None
        except Exception as exc:
            #print(exc)
            node_status = None

        if (not node_status) or ('node' not in node_status) or ('status' not in node_status):
            return None

        node_stopped = False
        if not node_status['status']:
            node_stopped = True

        return node_stopped

    def request_status(self, node_id):
        status_url = self.ctrl_base_url
        if not status_url.endswith('/'):
            status_url += '/'
        status_url += '_status'

        try:
            status_url += '?node=' + str(int(node_id))
        except:
            return None

        try:
            response = urllib2.urlopen(status_url)
            node_result = response.read()
            node_status = json.loads(node_result)
            if type(node_status) is not dict:
                node_status = None
        except Exception as exc:
            #print(exc)
            return None

        if (not node_status) or ('node' not in node_status) or ('status' not in node_status):
            return None

        return node_status['status']

