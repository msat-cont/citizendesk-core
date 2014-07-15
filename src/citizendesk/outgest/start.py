#!/usr/bin/env python
#
# Citizen Desk
#

DAEMON_NAME = 'Citizen Desk outflow server'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9061

MONGODB_SERVER_HOST = 'localhost'
MONGODB_SERVER_PORT = 27017

DB_NAME = 'citizendesk'

ALLOWED_CLIENTS = ['127.0.0.1']

LOG_PATH = '/opt/citizendesk/log/citizendesk/outer_ifce.log'
PID_PATH = '/opt/citizendesk/run/outer_ifce.pid'
HOME_DIR = '/tmp'

CONFIG_PATH = '/opt/citizendesk/etc/citizendesk/outer_ifce.yaml'

import os, sys, datetime, json, logging
import time, atexit, signal
import argparse
import pwd, grp

class ConnectParams():
    def __init__(self):
        self.web_host = DEFAULT_HOST
        self.web_port = DEFAULT_PORT
        self.mongo_host = MONGODB_SERVER_HOST
        self.mongo_port = MONGODB_SERVER_PORT
        self.db_name = DB_NAME
        self.log_path = None
        self.pid_path = None
        self.allowed = ALLOWED_CLIENTS
        self.home_dir = HOME_DIR
        self.daemonize = False
        self.user_id = None
        self.group_id = None
        self.config_path = CONFIG_PATH

    def use_specs(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('-w', '--web_host', help='web host of this controller, e.g. ' + str(DEFAULT_HOST), default=DEFAULT_HOST)
        parser.add_argument('-p', '--web_port', help='web port of this controller, e.g. ' + str(DEFAULT_PORT), type=int, default=DEFAULT_PORT)

        parser.add_argument('-m', '--mongo_host', help='host of mongodb, e.g. ' + str(MONGODB_SERVER_HOST), default=MONGODB_SERVER_HOST)
        parser.add_argument('-o', '--mongo_port', help='port of mongodb, e.g. ' + str(MONGODB_SERVER_PORT), type=int, default=MONGODB_SERVER_PORT)
        parser.add_argument('-b', '--db_name', help='database name, e.g. ' + str(DB_NAME), default=DB_NAME)

        parser.add_argument('-c', '--config_path', help='config path, e.g. ' + str(CONFIG_PATH), default=CONFIG_PATH)

        parser.add_argument('-l', '--log_path', help='path to log file, e.g. ' + str(LOG_PATH))
        parser.add_argument('-i', '--pid_path', help='path to pid file, e.g. ' + str(PID_PATH))

        parser.add_argument('-a', '--allowed', help='path to file with ip addresses of allowed clients')

        parser.add_argument('-d', '--daemonize', help='daemonize the process', action='store_true')
        parser.add_argument('-u', '--user', help='user of the daemon process')
        parser.add_argument('-g', '--group', help='group of the daemon process')

        args = parser.parse_args()
        if args.web_host:
            self.web_host = args.web_host
        if args.web_port:
            self.web_port = int(args.web_port)

        if args.mongo_host:
            self.mongo_host = args.mongo_host
        if args.mongo_port:
            self.mongo_port = int(args.mongo_port)
        if args.db_name:
            self.db_name = args.db_name

        if args.config_path:
            self.config_path = args.config_path

        if args.log_path:
            self.log_path = args.log_path
        if args.pid_path:
            self.pid_path = args.pid_path

        if args.user:
            try:
                user_info = pwd.getpwnam(args.user)
                self.user_id = int(user_info.pw_uid)
                if user_info.pw_dir and os.path.exists(user_info.pw_dir):
                    self.home_dir = user_info.pw_dir
            except:
                sys.stderr.write('can not find the daemon user\n')
                os._exit(1)

        if args.group:
            try:
                group_info = grp.getgrnam(args.group)
                self.group_id = int(group_info.gr_gid)
            except:
                sys.stderr.write('can not find the daemon group\n')
                os._exit(1)

        if args.daemonize:
            self.daemonize = True
            correct = True
            if not self.log_path:
                sys.stderr.write('log path not provided\n')
                correct = False
            if not self.pid_path:
                sys.stderr.write('pid path not provided\n')
                correct = False
            if not self.user_id:
                sys.stderr.write('user name not provided\n')
                correct = False
            if not self.group_id:
                sys.stderr.write('group name not provided\n')
                correct = False
            if not correct:
                os._exit(1)

        if args.allowed:
            try:
                self.allowed = []
                fh = open(args.allowed, 'r')
                while True:
                    line = fh.readline()
                    if not line:
                        break
                    line = line.split('#')[0].strip()
                    if not line:
                        continue
                    self.allowed.append(line)
                fh.close()
            except:
                self.allowed = ALLOWED_CLIENTS

    def get_web_host(self):
        return self.web_host

    def get_web_port(self):
        return self.web_port

    def get_mongo_host(self):
        return self.mongo_host

    def get_mongo_port(self):
        return self.mongo_port

    def get_db_name(self):
        return self.db_name

    def get_config_path(self):
        return self.config_path

    def get_log_path(self):
        return self.log_path

    def get_pid_path(self):
        return self.pid_path

    def get_home_dir(self):
        return self.home_dir

    def to_daemonize(self):
        return self.daemonize

    def get_user_id(self):
        return self.user_id

    def get_group_id(self):
        return self.group_id

    def get_allowed_ips(self):
        return self.allowed

params = ConnectParams()

def run_server():
    global params

    server_address = (params.get_web_host(), params.get_web_port())
    mongo_address = (params.get_mongo_host(), params.get_mongo_port())
    run_flask(params.get_db_name(), server=server_address, mongo=mongo_address, config_path=params.get_config_path(), debug=False)

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(file_dir)))

    try:
        from citizendesk.common.utils import setup_logger, get_logger, set_allowed_ips
        from citizendesk.common.utils import set_pid_path, set_daemon_name
        from citizendesk.common.utils import daemonize, set_user, cleanup, exit_handler
        from citizendesk.outgest.run import run_flask
    except:
        sys.stderr.write('citizen modules not installed\n')
        os._exit(1)

    params.use_specs()
    setup_logger(params.get_log_path())
    set_pid_path(params.get_pid_path())
    set_allowed_ips(params.get_allowed_ips())
    set_daemon_name(DAEMON_NAME)

    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    if params.to_daemonize():
        daemonize(params.get_home_dir(), params.get_pid_path())
        set_user(params.get_user_id(), params.get_group_id(), params.get_pid_path())

    logger = get_logger()
    try:
        logger.info('starting the ' + str(DAEMON_NAME))
        run_server()
    except Exception as exc:
        logger.error('can not start the ' + str(DAEMON_NAME) + ': ' + str(exc))
        cleanup(1)

