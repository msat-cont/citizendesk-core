#!/usr/bin/env python
#
# Citizen Desk
#

MONGODB_SERVER_HOST = 'localhost'
MONGODB_SERVER_PORT = 27017

DB_NAME = 'citizendesk'
NEWSTWISTER_URL = 'http://localhost:9054/'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9060

import os, sys, datetime, json, logging
from collections import namedtuple
try:
    from flask import Flask, request, Blueprint, make_response
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)
MongoClient = None
try:
    from pymongo import MongoClient
except:
    MongoClient = None
if not MongoClient:
    try:
        from pymongo import Connection as MongoClient
    except:
        MongoClient = None
if not MongoClient:
    logging.error('MongoDB support is not installed')
    os._exit(1)

class HTTPMethodOverrideMiddleware(object):
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS',
        'SEARCH'
    ])
    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if method in self.allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method
        if method in self.bodyless_methods:
            environ['CONTENT_LENGTH'] = '0'
        return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

@app.before_request
def check_client():
    from citizendesk.common.utils import get_logger, get_client_ip, get_allowed_ips

    logger = get_logger()
    client_ip = get_client_ip()

    message = '' + str(request.method) + ' request on ' + str(request.url) + ', by ' + str(get_client_ip())

    allowed_ips = get_allowed_ips()
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed ' + message)
            return make_response('Client not allowed\n\n', 403,)

    logger.info('allowed ' + message)

def prepare_reporting(mongo_addr, dbname, newstwister_url):
    from citizendesk.common.dbc import mongo_dbs
    from citizendesk.feeds.config import set_config
    import citizendesk.feeds.twt.dispatch as twt_dispatch

    mongo_dbs.set_dbname(dbname)
    DbHolder = namedtuple('DbHolder', 'db')
    mongo_dbs.set_db(DbHolder(db=MongoClient(mongo_addr[0], mongo_addr[1])[mongo_dbs.get_dbname()]))

    set_config('newstwister_url', newstwister_url)

    twt_dispatch.setup_blueprints(app)

@app.errorhandler(404)
def page_not_found(error):
    from citizendesk.common.utils import get_client_ip
    from citizendesk.common.utils import get_logger

    logger = get_logger()
    logger.info('page not found: ' + str(request.method) + ' on ' + str(request.url) + ', by ' + str(get_client_ip()))

    return 'page not found', 404

def run_flask(dbname, server, mongo, newstwister_url, debug=False):
    prepare_reporting(mongo, dbname, newstwister_url)
    app.run(host=server[0], port=server[1], debug=debug)

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(file_dir)))
    from citizendesk.common.utils import setup_logger

    default_server = (DEFAULT_HOST, DEFAULT_PORT)
    default_mongo = (MONGODB_SERVER_HOST, MONGODB_SERVER_PORT)

    setup_logger()
    run_flask(DB_NAME, server=default_server, mongo=default_mongo, newstwister_url=NEWSTWISTER_URL, debug=True)

