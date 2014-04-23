#!/usr/bin/env python

import os, sys, datetime, json, logging
import urllib, urllib2
import copy

class NewstwisterConnector():
    def __init__(self, base_url):
        self.ctrl_base_url = base_url

    def request_search(self, user_id, request_id, search_spec):
        search_url = self.ctrl_base_url
        if not search_url.endswith('/'):
            search_url += '/'
        search_url += '_search'

        params = {}
        params['user_id'] = user_id
        params['request_id'] = request_id
        params['search_spec'] = search_spec

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

    def request_start(self, endpoint_id, oauth_params, filter_params):
        # make connection to twister_main
        # take response from connection

        start_url = self.ctrl_base_url
        if not start_url.endswith('/'):
            start_url += '/'
        start_url += '_start'

        params = {}
        params['oauth_info'] = oauth_params
        params['stream_filter'] = filter_params
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

