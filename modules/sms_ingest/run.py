#!/usr/bin/env python

import os, sys
try:
    from flask import Flask, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    sys.exit(1)

from connect import sms_take

app = Flask(__name__)
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)

