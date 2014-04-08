#!/usr/bin/env python
#
# Config data for feeds
#

config = {}

def set_config(key, value):
    global config

    config[key] = value

def get_config(key):
    global config

    if key in config:
        return None

    return config[key]

