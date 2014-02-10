#!/usr/bin/env python

import os, sys
try:
    from flask import Flask, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    sys.exit(1)

DB_NAME = 'citizen_reports'

from reporting.dbc import mongo_dbs
from sms_ingest.connect import sms_take

app = Flask(__name__)

def prepare_reporting(dbname):
    mongo_dbs.set_dbname(dbname)
    app.config['MONGO_CITIZENDESK_DBNAME'] = mongo_dbs.get_dbname()
    mongo_dbs.set_db(PyMongo(app, config_prefix='MONGO_CITIZENDESK'))

    app.register_blueprint(sms_take)

@app.errorhandler(404)
def page_not_found(error):

    print(request.url)
    print('\n\n')
    print(request.method)
    print('\n\n')
    print(request.path)
    print('\n\n')
    print(request.full_path)
    print('\n\n')
    print(request.content_type)
    print('\n\n')
    print(request.get_data())
    print('\n\n')

    return 'bum, page_not_found.html', 404

def run_flask(dbname, host='localhost', port=5000, lockfile='', debug=False):
    prepare_reporting(dbname)
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_flask(DB_NAME, host='localhost', port=5000, lockfile='', debug=True)

