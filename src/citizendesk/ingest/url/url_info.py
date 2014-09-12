#!/usr/bin/env python

import datetime
import re, urllib
import BeautifulSoup

OGPROPS = re.compile(r'^og')

def get_page_info(url):

    required_info = {
        'url': '',
        'date': '',
        'title': '',
        'image': [],
        'description': '',
        'site_icon': '',
        'content_type': '',
        'type': '',
        'language': '',
    }

    og_properties = {
        'og:url': 'url',
        'og:title': 'title',
        'og:image': 'image',
        'og:description': 'description',
        'og:type': 'type',
    }

    try:
        fh = urllib.urlopen(url)
        if fh.headers.type:
            required_info['content_type'] = fh.headers.type.split(';')[0].strip().lower()
        pd = fh.read()
        fh.close()
    except Exception as exc:
        return (False, 'can not open url: ' + str(exc))

    bs = BeautifulSoup.BeautifulSoup(pd)
    if (not bs) or (not bs.html) or (not bs.html.head):
        bs = BeautifulSoup.BeautifulStoneSoup(pd)

    if bs and bs.html and bs.html.head:
        ogs = bs.html.head.findAll(property=OGPROPS)

        for og_part in ogs:
            if not og_part['content']:
                continue
            if not og_part['property'] in og_properties:
                continue
            use_property = og_properties[og_part['property']]
            if not use_property in required_info:
                continue
            if type(required_info[use_property]) is list:
                required_info[use_property].append(og_part['content'])
            else:
                required_info[use_property] = og_part['content']

    if not required_info['url']:
        required_info['url'] = url

    if not required_info['date']:
        required_info['date'] = datetime.datetime.utcnow()

    if not required_info['title']:
        if bs and bs.html and bs.html.head and bs.html.head.title and bs.html.head.title.text:
            required_info['title'] = bs.html.head.title.text
        else:
            pass # take end of url path (w/o params, and w/o .suffix) or full domain if not path

    for one_meta in bs.html.head.findAll('meta'):
        if not one_meta:
            continue
        if not 'content' in one_meta.attrMap:
            continue
        if not one_meta.attrMap['content']:
            continue

        if not required_info['description']:
            if ('name' in one_meta.attrMap) and one_meta.attrMap['name'] and (one_meta.attrMap['name'].lower() == 'description'):
                required_info['description'] = one_meta.attrMap['content']

        if not required_info['language']:
            if ('http-equiv' in one_meta.attrMap) and one_meta.attrMap['http-equiv'] and (one_meta.attrMap['http-equiv'].lower() == 'content-language'):
                # {u'content': u'cs', u'http-equiv': u'content-language'}
                required_info['language'] = one_meta.attrMap['content']

        if not required_info['content_type']:
            if ('http-equiv' in one_meta.attrMap) and one_meta.attrMap['http-equiv'] and (one_meta.attrMap['http-equiv'].lower() == 'content-type'):
                try:
                    # {u'content': u'text/html; charset=%SOUP-ENCODING%', u'http-equiv': u'content-type'}
                    required_info['content_type'] = one_meta.attrMap['content'].split(';')[0].strip().lower()
                except:
                    pass

    if not required_info['description']:
        try:
            required_info['description'] = bs.html.head.title.text
        except:
            pass

    if not required_info['site_icon']:
        # link/rel/shortcut icon
        pass

    if not required_info['image']:
        # img/src
        pass

    return (True, required_info)

def test():

    url = 'http://tech.ihned.cz/testy/c1-62719620-sencor-element-destroyer-odolny-telefon-jsme-koupali-i-prejeli-autem-prezil-vsechno'
    res = get_page_info(url)
    print(res)


if __name__ == '__main__':
    test()

