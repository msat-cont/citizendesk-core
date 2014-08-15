#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
# fill in the media-services sets that shoud be saved into DB
# it shoud be put into "srvcs_spec.py" file, alike:

services_info = [
    {
        'title': 'service name',
        'description': 'service description',
        'notice': 'comment on the service',
        'type': 'image',
        'active': True,
        'spec': {}, # ways to connect to the service
    },
]

'''

# predefined services

services_info = [
    {
        'type': 'image',
        'site': 'http://tineye.com/',
        'title': 'TinEye',
        'description': 'Reverse image search by Id\xc3\xa9e',
        'notice': 'indexed usually with a delay',
        'spec': {
            'method': 'client_get',
            'http': 'http://www.tineye.com/search?url=<<img_link_url_encoded>>',
            'https': 'https://www.tineye.com/search?url=<<img_link_url_encoded>>',
            'parameters': {
                '<<img_link_url_encoded>>': 'url_encoded_img_link',
            },
        },
        'active': True,
    },
    {
        'type': 'image',
        'site': 'http://images.google.com/',
        'title': 'Google Images',
        'description': 'Reverse image search by Google',
        'notice': 'usually including last news pictures',
        'spec': {
            'method': 'client_get',
            'http': 'http://images.google.com/searchbyimage?image_url=<<img_link_url_encoded>>',
            'https': 'https://images.google.com/searchbyimage?image_url=<<img_link_url_encoded>>',
            'parameters': {
                '<<img_link_url_encoded>>': 'url_encoded_img_link',
            },
        },
        'active': True,
    },
    {
        'type': 'image',
        'site': 'http://fotoforensics.com/',
        'title': 'FotoForensics',
        'description': 'Error Level Analysis by Hacker Factor',
        'notice': 'png, jpeg only, not explicit pictures',
        'spec': {
            'method': 'client_get',
            'http': 'http://fotoforensics.com/upload-url.php?url=<<img_link_url_encoded>>',
            'parameters': {
                '<<img_link_url_encoded>>': 'url_encoded_img_link',
            },
        },
        'active': True,
    },
    {
        'type': 'image',
        'site': 'regex.info/exif.cgi',
        'title': 'Jeffrey\'s Exif Viewer',
        'description': 'Exif (Image Data) Viewer by Jeffrey Friedl',
        'notice': '',
        'spec': {
            'method': 'client_get',
            'http': 'http://regex.info/exif.cgi?imgurl=<<img_link_url_encoded>>',
            'parameters': {
                '<<img_link_url_encoded>>': 'url_encoded_img_link',
            },
        },
        'active': True,
    },
    {
        'type': 'image',
        'site': 'http://metapicz.com/',
        'title': 'Metapicz Exif Viewer',
        'description': 'Metadata and Exif Viewer by Securo',
        'notice': '',
        'spec': {
            'method': 'client_get',
            'http': 'http://metapicz.com/?imgsrc=<<img_link_url_encoded>>',
            'parameters': {
                '<<img_link_url_encoded>>': 'url_encoded_img_link',
            },
        },
        'active': True,
    },
]

