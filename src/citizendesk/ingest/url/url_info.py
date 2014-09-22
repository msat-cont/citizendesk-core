#!/usr/bin/env python

import datetime
import re
import BeautifulSoup

try:
    from urllib.parse import urlparse, urlunparse, urljoin, unquote_plus
    from urllib.request import Request, urlopen
except:
    from urlparse import urlparse, urlunparse, urljoin
    from urllib import unquote_plus
    from urllib2 import Request, urlopen

OGPROPS = re.compile(r'^og')
TWPROPS = re.compile(r'^twitter')
ICORELS = re.compile(r'^shortcut icon')
MAX_IMG_LINKS_TAKE = 10
REQUEST_TIMEOUT = 30

def get_page_info(url):

    try:
        url_parsed = urlparse(url, scheme='http')
        url = urlunparse(url_parsed)
    except Exception as exc:
        return (False, 'can not parse url: ' + str(exc))

    url_subs = url

    required_info = {
        'url': '',
        'author': '',
        'date': '',
        'title': '',
        'image': [],
        'description': '',
        'site_icon': '',
        'content_type': '',
        'type': '',
        'language': '',
        'feed_name': '',
        'domain_name': '',
    }

    og_properties = {
        'og:url': 'url',
        'og:title': 'title',
        'og:image': 'image',
        'og:description': 'description',
        'og:type': 'type',
    }

    tw_properties = {
        'twitter:site': 'feed_name',
    }

    try:
        rq = Request(url)
        rq.add_header('User-Agent', 'citizen desk core')
        fh = urlopen(rq, timeout=REQUEST_TIMEOUT)
        if not fh:
            return (False, 'unopened url')
        if fh.headers and hasattr(fh.headers, 'type') and fh.headers.type:
            required_info['content_type'] = fh.headers.type.split(';')[0].strip().lower()
        url_subs = fh.geturl()
        pd = fh.read()
        fh.close()
    except Exception as exc:
        return (False, 'can not open url: ' + str(exc))

    if not url_subs:
        url_subs = url
    else:
        url = url_subs

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
                if 'image' == use_property:
                    required_info[use_property].append(urljoin(url_subs, og_part['content']))
                else:
                    required_info[use_property].append(og_part['content'])
            else:
                required_info[use_property] = og_part['content']

        tws = bs.html.head.findAll(property=TWPROPS)
        for tw_part in tws:
            if not tw_part['content']:
                continue
            if not tw_part['property'] in tw_properties:
                continue
            use_property = tw_properties[tw_part['property']]
            if not use_property in required_info:
                continue
            if type(required_info[use_property]) is list:
                required_info[use_property].append(tw_part['content'])
            else:
                required_info[use_property] = tw_part['content']

    if not required_info['url']:
        required_info['url'] = url

    if not required_info['date']:
        required_info['date'] = datetime.datetime.utcnow()

    if not required_info['title']:
        if bs and bs.html and bs.html.head and bs.html.head.title and bs.html.head.title.text:
            required_info['title'] = bs.html.head.title.text
        else:
            # take end of url path (w/o params, and w/o .suffix) or full domain if not path
            end_path_part = ''
            path_parts = url_parsed.path.split('/')
            path_parts.reverse()
            for one_part in path_parts:
                one_part = unquote_plus(one_part).split('.')[0].strip()
                if one_part:
                    end_path_part = one_part
                    break
            if not end_path_part:
                end_path_part = url_parsed.netloc.split(':')[0].strip()
            if end_path_part:
                required_info['title'] = end_path_part

    if bs and bs.html and bs.html.head:
        for one_meta in bs.html.head.findAll('meta'):
            if not one_meta:
                continue
            if not one_meta.attrMap:
                continue
            if not 'content' in one_meta.attrMap:
                continue
            if not one_meta.attrMap['content']:
                continue

            if not required_info['description']:
                if ('name' in one_meta.attrMap) and one_meta.attrMap['name'] and (one_meta.attrMap['name'].lower() == 'description'):
                    required_info['description'] = one_meta.attrMap['content']

            if not required_info['author']:
                if ('name' in one_meta.attrMap) and one_meta.attrMap['name'] and (one_meta.attrMap['name'].lower() == 'author'):
                    author_parts = one_meta.attrMap['content'].split(':')
                    author_parts.reverse()
                    for one_auth_part in author_parts:
                        one_auth_part = one_auth_part.strip()
                        if one_auth_part:
                            required_info['author'] = one_auth_part
                            break

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

    if (not required_info['site_icon']) and bs and bs.html and bs.html.head:
        # link/rel/shortcut+icon
        icos = bs.html.head.findAll(rel=ICORELS)

        for ico_part in icos:
            if not ico_part:
                continue
            if not 'href' in ico_part:
                continue
            if not ico_part['href']:
                continue
            ico_link = urljoin(url_subs, ico_part['href'])
            if ico_link:
                required_info['site_icon'] = ico_link
                break

    if (not required_info['site_icon']):
        try:
            required_info['site_icon'] = 'http://g.etfv.co/' + url
        except:
            required_info['site_icon'] = 'http://g.etfv.co/' + 'http'

    if (len(required_info['image']) < MAX_IMG_LINKS_TAKE) and bs and bs.html and bs.html.body:
        # img/src
        for one_img in bs.html.body.findAll('img'):
            if not one_img:
                continue
            if not 'src' in one_img:
                continue
            if not one_img['src']:
                continue
            one_img_link = urljoin(url_subs, one_img['src'])

            if one_img_link:
                required_info['image'].append(one_img_link)
                if len(required_info['image']) >= MAX_IMG_LINKS_TAKE:
                    break

    if required_info['url']:
        required_info['domain_name'] = urlparse(required_info['url']).netloc.split(':')[0].strip()

    return (True, required_info)

def test():

    url = 'https://www.sourcefabric.org/'
    res = get_page_info(url)
    print(res)


if __name__ == '__main__':
    test()

