#!/usr/bin/env python
#
# Citizen Desk
#

MONGODB_SERVER_HOST = 'localhost'
MONGODB_SERVER_PORT = 27017

DB_NAME = 'citizendesk'
LIVEBLOG_CONFIG_PATH = None

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9061

import os, sys, datetime, json, logging
from collections import namedtuple
try:
    import yaml
except:
    sys.stderr.write('Can not load YAML support\n')
    sys.exit(1)
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
    if (allowed_ips is not None) and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            logger.info('unallowed ' + message)
            return make_response('Client not allowed\n\n', 403,)

    logger.info('allowed ' + message)

def prepare_reporting(mongo_addr, dbname, liveblog_config_path):
    from citizendesk.common.utils import get_logger
    from citizendesk.common.dbc import mongo_dbs
    from citizendesk.feeds.config import set_config
    import citizendesk.outgest.dispatch as dispatch

    logger = get_logger()

    mongo_dbs.set_dbname(dbname)
    DbHolder = namedtuple('DbHolder', 'db')
    mongo_dbs.set_db(DbHolder(db=MongoClient(mongo_addr[0], mongo_addr[1])[mongo_dbs.get_dbname()]))

    '''
    if liveblog_config_path:
        try:
            lbhf = open(liveblog_config_path)
            liveblog_config_data = lbhf.read()
            lbhf.close()
            liveblog_yaml = yaml.load_all(liveblog_config_data)
            liveblog_config = liveblog_yaml.next()
            liveblog_yaml.close()
        except:
            logger.error('can not read liveblog config file: ' + str(liveblog_config_path))
            return False

        if ('allowed_ips' in liveblog_config) and liveblog_config['allowed_ips']:
            set_config('liveblog_allowed_ips', liveblog_config['allowed_ips'])
    '''

    dispatch.setup_blueprints(app)

    return True

@app.errorhandler(404)
def page_not_found(error):
    from citizendesk.common.utils import get_client_ip
    from citizendesk.common.utils import get_logger

    logger = get_logger()
    logger.info('page not found: ' + str(request.method) + ' on ' + str(request.url) + ', by ' + str(get_client_ip()))

    return 'page not found', 404

def run_flask(dbname, server, mongo, liveblog_config_path, debug=False):
    from citizendesk.common.utils import get_logger
    logger = get_logger()

    state = prepare_reporting(mongo, dbname, liveblog_config_path)
    if not state:
        logger.warning('quiting the feeds daemon for not successful startup')
        return

    app.run(host=server[0], port=server[1], debug=debug, threaded=True)

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(file_dir)))
    from citizendesk.common.utils import setup_logger

    default_server = (DEFAULT_HOST, DEFAULT_PORT)
    default_mongo = (MONGODB_SERVER_HOST, MONGODB_SERVER_PORT)

    setup_logger()
    run_flask(DB_NAME, server=default_server, mongo=default_mongo, liveblog_config_path=LIVEBLOG_CONFIG_PATH, debug=True)

