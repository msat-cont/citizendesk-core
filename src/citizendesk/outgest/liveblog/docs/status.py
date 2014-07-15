#!/usr/bin/env python
#
# corresponding parts of Citizen Desk output vs. Liveblog chaining
#

'''
blog/coverage list:
http://localhost/streams/liveblog/coverage
http://localhost/streams/liveblog/coverage?X-Filter=Title,Description
{
    total: 30
    limit: 30
    offset: 0
    BlogList:
    [
        {
            href: url to blog data, e.g. 'http://localhost/streams/liveblog/coverage/1'
            Description: string
            Title: string
        },
        ...
    ]
}

one blog/coverage:
http://localhost/streams/liveblog/coverage/1
http://localhost/streams/liveblog/coverage/1?asc=cId&cId.since=1100

necessary/should:

regarding CId:
*   created online from _updated datetime

{
'PostList':
[
{
    'CId': integer,
    'IsPublished': boolean,
    'Uuid': string,
    'DeletedOn': datetime, # should be totally omitted, if not deleted
    'Author': {'href': string},
    'Creator': {'href': string},
    'Type': {'Key': string},
    'Meta': string, # need not be in, but for SMS, it holds the editorial comments
    'ContentPlain': string, # need not be in
    'Content': string, # need not be in
    'Order': decimal, # need not be in
}
]
}

Author:
{
    'Source':
    {
        'Name': string,
    },
    'User':
    {
        'Uuid': string,
        'Cid': integer,
        'FirstName': string,
        'LastName': string,
        'Address': string,
        'PhoneNumber': string,
        'EMail': string,
        'MetaDataIcon':
        {
            'href': string,
        },
    }
}

Creator:
{
    'Uuid': string,
    'Cid': integer,
    'FirstName': string,
    'LastName': string,
    'Address': string,
    'PhoneNumber': string,
    'EMail': string,
    'MetaDataIcon':
    {
        'href': string,
    },
}

MetaDataIcon['href']:
{
    'Content':
    {
        'href': string,
    },
}

'''
