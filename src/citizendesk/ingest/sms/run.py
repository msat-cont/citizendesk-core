#!/usr/bin/env python
#
# Citizen Desk
#

MONGODB_SERVER_HOST = 'localhost'
MONGODB_SERVER_PORT = 27017

DEFAULT_PORT = 5001

import os, sys, datetime, json, logging
import atexit
from collections import namedtuple
try:
    from flask import Flask, request, Blueprint
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)
try:
    from pymongo import MongoClient
except:
    logging.error('MongoDB support is not installed')
    os._exit(1)

DB_NAME = 'citizendesk'

from citizendesk.common.dbc import mongo_dbs
from citizendesk.ingest.sms.connect import sms_take

app = Flask(__name__)

def prepare_reporting(dbname):
    mongo_dbs.set_dbname(dbname)
    DbHolder = namedtuple('DbHolder', 'db')
    mongo_dbs.set_db(DbHolder(db=MongoClient(MONGODB_SERVER_HOST, MONGODB_SERVER_PORT)[mongo_dbs.get_dbname()]))

    app.register_blueprint(sms_take)

@app.errorhandler(404)
def page_not_found(error):

    for part in [request.url, request.method, request.path, request.full_path, request.content_type, request.get_data()]:
        sys.stderr.write(str(part))
        sys.stderr.write('\n\n')

    return 'page_not_found.html', 404

def run_flask(dbname, host='localhost', port=DEFAULT_PORT, lockfile='', debug=False):
    prepare_reporting(dbname)
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_flask(DB_NAME, host='localhost', port=DEFAULT_PORT, lockfile='', debug=True)

