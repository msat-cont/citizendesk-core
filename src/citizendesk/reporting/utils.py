#!/usr/bin/env python
#
# Citizen Desk
#

try:
    from flask import request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

def get_conf(name):
    configs = {'local_ips':[]}
    if name in configs:
        return configs[name]
    return None

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
        if '10' == ip_parts[0]:
            return False
        if '172' == ip_parts[0]:
            if ip_parts[1].isdigit() and (16 <= int(ip_parts[1])) and (31 >= int(ip_parts[1])):
                return False
        if ('192' == ip_parts[0]) and ('168' == ip_parts[0]):
            return False

    local_ips = get_conf('local_ips')
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


