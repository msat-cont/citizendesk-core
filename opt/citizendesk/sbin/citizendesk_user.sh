#!/bin/sh

HOMEDIR=/opt/citizendesk
mkdir -p $HOMEDIR

addgroup --system citizendesk
adduser --system --home $HOMEDIR --no-create-home --ingroup dialout --disabled-login citizendesk

chown citizendesk $HOMEDIR
#chown citizendesk $HOMEDIR/*

