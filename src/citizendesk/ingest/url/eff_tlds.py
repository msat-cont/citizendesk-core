#!/usr/bin/env python

import codecs

COMMENT_TAG = '//'
ASCII_INT_TAG = 'xn--'
STAR_TAG = '*'
EXCL_TAG = '!'
DOMAIN_CON = '.'

def take_tlds_sets(dat_file_path):
    common = [] # standard effective TLDs
    starred = [] # starting with a *, meant that any domain part in the place of * is still common effective TLD
    excluded = [] # starting with an !, meant that the domain (after !) is not a common effective TLD (exception to the * case)

    try:
        dfh = codecs.open(dat_file_path, 'r', 'utf-8', errors='ignore')
    except:
        return None

    while True:
        line = dfh.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue
        if line.startswith(COMMENT_TAG):
            continue

        if line.startswith(STAR_TAG):
            line = line[len(STAR_TAG):].strip()
            if line:
                if line.startswith(DOMAIN_CON):
                    line = line[len(DOMAIN_CON):].strip()
                    if line:
                        starred.append(line)
            continue

        if line.startswith(EXCL_TAG):
            line = line[len(EXCL_TAG):]
            if line:
                excluded.append(line)
            continue

        common.append(line)

    try:
        dfh.close()
    except:
        pass

    return {
        'common': frozenset(common),
        'starred': frozenset(starred),
        'excluded': frozenset(excluded),
    }

def take_specific_domain(tlds, domain):
    if ASCII_INT_TAG in domain:
        try:
            domain = domain.decode('idna')
        except:
            pass

    domain_parts = domain.strip().split(DOMAIN_CON)
    if not domain_parts:
        return ''

    # is it of an excluded domain (from the starred domains)
    for ind in range(len(domain_parts)):
        domain_suffix = DOMAIN_CON.join(domain_parts[ind:])
        if not domain_suffix:
            continue
        if domain_suffix in tlds['excluded']:
            # the excluded domains are already the specific ones
            return domain_suffix

    # is it of an starred domain
    for ind in range(len(domain_parts)):
        domain_suffix = DOMAIN_CON.join(domain_parts[ind:])
        if not domain_suffix:
            continue
        if domain_suffix in tlds['starred']:
            # even the one-longer suffix is still common for a starred domain
            ind_spec = ind - 2
            if ind_spec < 0:
                ind_spec = 0
            return DOMAIN_CON.join(domain_parts[ind_spec:])

    # is it of a common domain
    for ind in range(len(domain_parts)):
        domain_suffix = DOMAIN_CON.join(domain_parts[ind:])
        if not domain_suffix:
            continue
        if domain_suffix in tlds['common']:
            # the one-longer suffix is the specific one for a common domain
            ind_spec = ind - 1
            if ind_spec < 0:
                ind_spec = 0
            return DOMAIN_CON.join(domain_parts[ind_spec:])

    # when the common domain not found
    ind_spec = len(domain_parts) - 2
    if ind_spec < 0:
        ind_spec = 0
    return DOMAIN_CON.join(domain_parts[ind_spec:])

def test(dat_file_path):
    test_names = [
        'm.ihned.cz',
        'www.bbc.co.uk',
        'www.xn--alliancefranaise-npb.nu',
        'www.city.kawasaki.jp',
        'www.this.that.kawasaki.jp'
    ]

    tlds = take_tlds_sets(dat_file_path)
    if not tlds:
        print('no tlds')
    else:
        for one_name in test_names:
            dom_spec = take_specific_domain(tlds, one_name)
            print(dom_spec)

if __name__ == '__main__':
    test('effective_tld_names.dat')

