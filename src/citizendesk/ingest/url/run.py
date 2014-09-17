#!/usr/bin/env python
#
# Citizen Desk
#

MONGODB_SERVER_HOST = 'localhost'
MONGODB_SERVER_PORT = 27017

DB_NAME = 'citizendesk'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9071

import os, sys, datetime, json, logging
from collections import namedtuple
try:
    from flask import Flask, request, Blueprint
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

app = Flask(__name__)

def prepare_reporting(mongo_addr, dbname, tlds_path):
    from citizendesk.common.dbc import mongo_dbs
    from citizendesk.ingest.url.utils import set_effective_tlds
    from citizendesk.ingest.url.connect import setup_blueprints

    mongo_dbs.set_dbname(dbname)
    DbHolder = namedtuple('DbHolder', 'db')
    mongo_dbs.set_db(DbHolder(db=MongoClient(mongo_addr[0], mongo_addr[1])[mongo_dbs.get_dbname()]))

    set_effective_tlds(tlds_path)
    setup_blueprints(app)

@app.errorhandler(404)
def page_not_found(error):
    from citizendesk.common.utils import get_client_ip
    from citizendesk.common.utils import get_logger

    logger = get_logger()

    logger.info('page not found: ' + str(request.method) + ' on ' + str(request.url) + ', by ' + str(get_client_ip()))
    return 'page not found', 404

def run_flask(dbname, server, mongo, tlds_path, debug=False):
    prepare_reporting(mongo, dbname, tlds_path)
    app.run(host=server[0], port=server[1], debug=debug, threaded=True)

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(os.path.dirname(os.path.dirname(file_dir)))
    from citizendesk.common.utils import setup_logger

    default_server = (DEFAULT_HOST, DEFAULT_PORT)
    default_mongo = (MONGODB_SERVER_HOST, MONGODB_SERVER_PORT)

    setup_logger()
    run_flask(DB_NAME, server=default_server, mongo=default_mongo, tlds_path=None, debug=True)

