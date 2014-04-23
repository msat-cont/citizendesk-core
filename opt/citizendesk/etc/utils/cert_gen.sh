#!/bin/sh
#
# generating a cert for nginx under a testing deployment
#

openssl req -new -x509 -keyout nginx.pem -out nginx.pem -days 365 -nodes


