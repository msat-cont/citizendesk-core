#!/usr/bin/env python
#
# Citizen Desk
#

import os, sys, time, signal
import logging, logging.handlers

try:
    from flask import request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    os._exit(1)

logger = logging.getLogger()
allowed_ips = ['127.0.0.1']

def setup_logger(log_path=None):
    global logger

    while logger.handlers:
        logger.removeHandler(logger.handlers[-1])

    formatter = logging.Formatter("%(levelname)s [%(asctime)s]: %(message)s")

    if log_path:
        fh = logging.handlers.WatchedFileHandler(log_path)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    else:
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    logger.setLevel(logging.INFO)

def get_logger():
    global logger
    return logger

def get_local_ips():
    # if we should have local ips out of the standard ranges
    return []

def set_allowed_ips(addr_list):
    global allowed_ips
    allowed_ips = addr_list if (type(addr_list) is list) else [addr_list]

def get_allowed_ips():
    global allowed_ips
    return allowed_ips

def is_remote_ip(ip_addr):
    if not ip_addr:
        False
    ip_addr = ip_addr.strip()
    if not ip_addr:
        False

    if ip_addr.startswith('fc00::'):
        return False

    ip_parts = ip_addr.split('.')
    if 4 == len(ip_parts):
        if '127' == ip_parts[0]:
            return False
        if '10' == ip_parts[0]:
            return False
        if '172' == ip_parts[0]:
            if ip_parts[1].isdigit() and (16 <= int(ip_parts[1])) and (31 >= int(ip_parts[1])):
                return False
        if ('192' == ip_parts[0]) and ('168' == ip_parts[0]):
            return False

    local_ips = get_local_ips()
    if local_ips and (ip_addr in local_ips):
        return False

    return True

def get_client_ip():

    remote_ip = ''

    for header_test in ['x-forwarded-for']:
        for cur_header in request.headers:
            if (1 < len(cur_header)) and cur_header[0] and (header_test == cur_header[0].lower()):
                got_remote_ips = [x.strip() for x in cur_header[1].split(',') if x]
                cur_ip_rank = len(got_remote_ips) - 1
                while cur_ip_rank >= 0:
                    one_rem_ip = got_remote_ips[cur_ip_rank]
                    cur_ip_rank -= 1
                    if not one_rem_ip:
                        continue
                    remote_ip = one_rem_ip
                    if is_remote_ip(one_rem_ip):
                        break
                break
        if remote_ip:
            break

    if not remote_ip:
        for header_test in ['http_client_ip', 'x-real-ip']:
            for cur_header in request.headers:
                if (1 < len(cur_header)) and cur_header[0] and (header_test == cur_header[0].lower()):
                    remote_ip = cur_header[1].strip()
                    break
            if remote_ip:
                break

    if not remote_ip:
        remote_ip = request.remote_addr

    return remote_ip

def get_boolean(value):
    if value is None:
        return None

    if not value:
        return False
    if type(value) is bool:
        return value

    if value in [0, '0']:
        return False
    if value in [1, '1']:
        return True

    if type(value) in [str, unicode]:
        if value.startswith('t'):
            return True
        if value.startswith('T'):
            return True
        if value.startswith('f'):
            return False
        if value.startswith('F'):
            return False

    return None

def get_sort(param):
    def_list = []

    if not param:
        return def_list

    try:
        item_set = param.split(',')
    except:
        return def_list

    for item in item_set:
        if not item:
            continue
        parts = item.split(':')
        if 2 != len(parts):
            continue
        if not parts[0]:
            continue
        if not parts[1]:
            continue
        order = None
        if parts[1][0] in ['1', '+', 'a', 'A']:
            order = 1
        if parts[1][0] in ['0', '-', 'd', 'D']:
            order = -1
        if not order:
            continue

        def_list.append((parts[0], order))

    return def_list

def daemonize(work_dir, pid_path):
    global logger

    UMASK = 022

    if (hasattr(os, 'devnull')):
       REDIRECT_TO = os.devnull
    else:
       REDIRECT_TO = '/dev/null'

    try:
        pid = os.fork()
    except OSError, e:
        logger.error('can not daemonize: %s [%d]' % (e.strerror, e.errno))
        logging.shutdown()
        cleanup(1)

    if (pid != 0):
        os._exit(0)

    os.setsid()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    try:
        pid = os.fork()
    except OSError, e:
        logger.error('can not daemonize: %s [%d]' % (e.strerror, e.errno))
        logging.shutdown()
        cleanup(1)

    if (pid != 0):
        os._exit(0)

    try:
        os.chdir(work_dir)
        os.umask(UMASK)
    except OSError, e:
        logger.error('can not daemonize: %s [%d]' % (e.strerror, e.errno))
        logging.shutdown()
        cleanup(1)

    try:
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(REDIRECT_TO, 'r')
        so = file(REDIRECT_TO, 'a+')
        se = file(REDIRECT_TO, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    except OSError, e:
        logger.error('can not daemonize: %s [%d]' % (e.strerror, e.errno))
        logging.shutdown()
        cleanup(1)

    if pid_path is None:
        logger.warning('no pid file path provided')
    else:
        try:
            fh = open(pid_path, 'w')
            fh.write(str(os.getpid()) + '\n')
            fh.close()
        except Exception:
            logger.error('can not create pid file: ' + str(pid_path))
            logging.shutdown()
            cleanup(1)

def set_user(user_id, group_id, pid_path):
    global logger

    if (user_id is not None) and (str(user_id) != '0'):
        if (pid_path is not None) and os.path.exists(pid_path):
            try:
                os.chown(pid_path, user_id, -1)
            except OSError, e:
                logger.warning('can not set pid file owner: %s [%d]' % (e.strerror, e.errno))

    if group_id is not None:
        try:
            os.setgid(group_id)
        except Exception as e:
            logger.error('can not set group id: %s [%d]' % (e.strerror, e.errno))
            cleanup(1)

    if user_id is not None:
        try:
            os.setuid(user_id)
        except Exception as e:
            logger.error('can not set user id: %s [%d]' % (e.strerror, e.errno))
            cleanup(1)

def cleanup(status=0):
    global logger

    logger.info('stopping the ' + str(get_daemon_name()))

    pid_path = get_pid_path()
    if pid_path is not None:
        try:
            fh = open(pid_path, 'w')
            fh.write('')
            fh.close()
        except Exception:
            logger.warning('can not clean pid file: ' + str(pid_path))

        if os.path.isfile(pid_path):
            try:
                os.unlink(pid_path)
            except Exception:
                pass

    logging.shutdown()
    os._exit(status)

def exit_handler(signal_number, frame):
    cleanup()

saved_pid_path = None

def set_pid_path(pid_path):
    global saved_pid_path
    saved_pid_path = pid_path

def get_pid_path():
    global saved_pid_path
    return saved_pid_path

saved_daemon_name = None

def set_daemon_name(daemon_name):
    global saved_daemon_name
    saved_daemon_name = daemon_name

def get_daemon_name():
    global saved_daemon_name
    return saved_daemon_name

