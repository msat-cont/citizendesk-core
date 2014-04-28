#!/usr/bin/env python
#
# corresponding parts of Citizen Desk output vs. Liveblog chaining
#

'''
blog/coverage list:
http://localhost:9060/outgest/liveblog/coverage

http://localhost:9060/outgest/liveblog/coverage?X-Filter=Title,Description
http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog?X-Filter=Title,Description
... list all active coverages
{
    total: 30
    limit: 30
    offset: 0
    BlogList:
    [
        {
            href: url to blog data, e.g. 'http://localhost:9060/streams/liveblog/coverage/1'
            Description: string
            Title: string
        },
        ...
    ]
}

one blog/coverage:
http://localhost:9060/streams/liveblog/coverage/1





'''

lb_blog_list = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/',
    'lb_content': {
        'BlogList': [{'href':'//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1'}, ...]
    },
    'cd_data': 'list of coverages',
}

lb_blog = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1',
    'lb_content': {
        'Id': '1',
        'IsLive': True,
        'Description': 'Welcome to our live election night coverage! ...',
        'EmbedConfig': None, # (string)
        'Title': 'Election Night 2013',
        'CreatedOn': '7/1/13 3:54 PM',
        'LiveOn': None, # not to include if None
        'UpdatedOn': None, # not to include if None
        'Post': {'href': '//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/'},
        'PostPublished': {'href': '//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/'},
    },
    'cd_data': 'taken from data fields of the coverage',
}

lb_blog_post_list = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post',
    'lb_content': {
        'PostList': [{'href':'//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/459'}, ...]
    },
    'cd_data': 'list of reports set to the coverage; have to find out how to only display unseen reports',
}

# http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/Published?asc=cId&cId.since=1100

'''
necessary/should:

regarding CId:
*   by s/t like publish_rank? depend on whether we need to propagate udates after having it published (probably yes);
    thus to have it only updated in published state, or having the 'publishing event' as a source of CId increase as well,
    i.e. any change whatsoever should increase it.

*   probably hash of the string-wise id

*   probably no order

*   we should probably save citizen info even when just partial as 'aliases',
    each citizen activity casts her/his shadow;
    for a proto-report, we probably should only create/cast the alias, when it gets taken.


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








by Liveblog:

curl -H 'Accept: application/json' "http://sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"
{"code":"400","message":"Input error","details":{"model":{"PersonIcon":{"Id":"Invalid person icon"}}}}

{
    "code":"400",
    "message":"Input error",
    "details":
    {
        "model":
        {
            "PersonIcon":
            {
                "Id":"Invalid person icon"
            }
        }
    }
}


curl -H 'Accept: application/json' "http://sourcefabric.superdesk.pro/resources/HR/Person/66/MetaData/Icon"
{"Id":"39","SizeInBytes":"165196","Name":"ksmllogo_iso_levea.jpg","Type":"image","CreatedOn":"10/15/13 1:17 PM","Content":{"href":"//sourcefabric.superdesk.pro/content/media_archive/image/000/39.ksmllogo_iso_levea.jpg"},"Creator":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66","Id":"66"},"Thumbnail":{"href":"//sourcefabric.superdesk.pro/content/media_archive/thumbnail/original/39.ksmllogo_iso_levea.jpg"}}

{
    "Id":"39",
    "SizeInBytes":"165196",
    "Name":"ksmllogo_iso_levea.jpg",
    "Type":"image",
    "CreatedOn":"10/15/13 1:17 PM",
    "Content":
    {
        "href":"//sourcefabric.superdesk.pro/content/media_archive/image/000/39.ksmllogo_iso_levea.jpg"
    },
    "Creator":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66",
        "Id":"66"
    },
    "Thumbnail":
    {
        "href":"//sourcefabric.superdesk.pro/content/media_archive/thumbnail/original/39.ksmllogo_iso_levea.jpg"
    }
}







curl -H 'Accept: application/json' -H 'X-Filter: *,User.*,Source.*' "http://sourcefabric.superdesk.pro/resources/Data/Collaborator/1"
{"Id":"1","Name":"google","Source":{"href":"//sourcefabric.superdesk.pro/resources/Data/Source/1","Id":"1","IsModifiable":"False","Key":"","Name":"google","Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/xml","Key":"xml"},"URI":{"href":"//sourcefabric.superdesk.pro/www.google.com"}},"Post":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1/Post/"},"PostPublished":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1/Post/Published"},"PostUnpublished":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1/Post/Unpublished"}}

{
    "Id":"1",
    "Name":"google",
    "Source":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Source/1",
        "Id":"1",
        "IsModifiable":"False",
        "Key":"",
        "Name":"google",
        "Type":
        {
            "href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/xml",
            "Key":"xml"
        },
        "URI":
        {
            "href":"//sourcefabric.superdesk.pro/www.google.com"
        }
    },
    "Post":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1/Post/"
    },
    "PostPublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1/Post/Published"
    },
    "PostUnpublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1/Post/Unpublished"
    }
}


curl -H 'Accept: application/json' -H 'X-Filter: *,User.*,Source.*' "http://sourcefabric.superdesk.pro/resources/Data/Collaborator/89"
{"Id":"89","Name":"SMS","Source":{"href":"//sourcefabric.superdesk.pro/resources/Data/Source/19","Id":"19","IsModifiable":"True","Name":"RightsCon","OriginURI":{"href":"//sourcefabric.superdesk.pro/RightsCon"},"Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/smsblog","Key":"smsblog"},"URI":{"href":"//sourcefabric.superdesk.pro/smsblog/RightsCon"}},"User":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84","Id":"84","Active":"True","Cid":"0","FirstName":"SMS","FullName":"SMS","Name":"SMS-77c4fa4b51e11927","PhoneNumber":"+420608577621","Uuid":"4c66a57c428e459da062b6734b9a7a31","CreatedOn":"2/18/14 1:20 PM","Type":{"href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms","Key":"sms"},"MetaDataIcon":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"}},"Post":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89/Post/"},"PostPublished":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89/Post/Published"},"PostUnpublished":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89/Post/Unpublished"}}

{
    "Id":"89",
    "Name":"SMS",
    "Source":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Source/19",
        "Id":"19",
        "IsModifiable":"True",
        "Name":"RightsCon",
        "OriginURI":
        {
            "href":"//sourcefabric.superdesk.pro/RightsCon"
        },
        "Type":
        {
            "href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/smsblog",
            "Key":"smsblog"
        },
        "URI":
        {
            "href":"//sourcefabric.superdesk.pro/smsblog/RightsCon"
        }
    },
    "User":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84",
        "Id":"84",
        "Active":"True",
        "Cid":"0",
        "FirstName":"SMS",
        "FullName":"SMS",
        "Name":"SMS-77c4fa4b51e11927",
        "PhoneNumber":"+420608577621",
        "Uuid":"4c66a57c428e459da062b6734b9a7a31",
        "CreatedOn":"2/18/14 1:20 PM",
        "Type":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms",
            "Key":"sms"
        },
        "MetaDataIcon":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"
        }
    },
    "Post":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89/Post/"
    },
    "PostPublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89/Post/Published"
    },
    "PostUnpublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89/Post/Unpublished"
    }
}


curl -H 'Accept: application/json' -H 'X-Filter: *' "http://sourcefabric.superdesk.pro/resources/HR/User/84"
{"Id":"84","Active":"True","Cid":"0","FirstName":"SMS","FullName":"SMS","Name":"SMS-77c4fa4b51e11927","PhoneNumber":"+420608577621","Uuid":"4c66a57c428e459da062b6734b9a7a31","CreatedOn":"2/18/14 1:20 PM","Type":{"href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms","Key":"sms"},"Role":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Role/"},"Right":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Right/"},"Post":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Post/"},"PostPublished":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Post/Published"},"PostUnpublished":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Post/Unpublished"},"Collaborator":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Collaborator/"},"Blog":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Blog/"},"BlogLive":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Blog/Live"},"Action":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Action/"},"MetaDataIcon":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"}}

{
    "Id":"84",
    "Active":"True",
    "Cid":"0",
    "FirstName":"SMS",
    "FullName":"SMS",
    "Name":"SMS-77c4fa4b51e11927",
    "PhoneNumber":"+420608577621",
    "Uuid":"4c66a57c428e459da062b6734b9a7a31",
    "CreatedOn":"2/18/14 1:20 PM",
    "Type":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms",
        "Key":"sms"
    },
    "Role":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Role/"
    },
    "Right":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Right/"
    },
    "Post":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Post/"
    },
    "PostPublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Post/Published"
    },
    "PostUnpublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Post/Unpublished"
    },
    "Collaborator":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Collaborator/"
    },
    "Blog":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Blog/"
    },
    "BlogLive":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Blog/Live"
    },
    "Action":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84/Action/"
    },
    "MetaDataIcon":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"
    }
}










curl -H 'Accept: application/json' -H 'X-Filter: *' "http://sourcefabric.superdesk.pro/resources/HR/User/66"
{"Id":"66","Active":"True","Cid":"0","EMail":"Janet.Admin@email.addr","FirstName":"Janet","FullName":"Janet Admin","LastName":"Admin","Name":"admin","CreatedOn":"10/14/13 9:22 AM","Type":{"href":"//sourcefabric.superdesk.pro/resources/HR/UserType/standard","Key":"standard"},"Role":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Role/"},"Right":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Right/"},"Post":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Post/"},"PostPublished":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Post/Published"},"PostUnpublished":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Post/Unpublished"},"Collaborator":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Collaborator/"},"Blog":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Blog/"},"BlogLive":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Blog/Live"},"Action":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Action/"},"MetaDataIcon":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/66/MetaData/Icon"}}

{
    "Id":"66",
    "Active":"True",
    "Cid":"0",
    "EMail":"Janet.Admin@email.addr",
    "FirstName":"Janet",
    "FullName":"Janet Admin",
    "LastName":"Admin",
    "Name":"admin",
    "CreatedOn":"10/14/13 9:22 AM",
    "Type":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/UserType/standard",
        "Key":"standard"
    },
    "Role":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Role/"
    },
    "Right":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Right/"
    },
    "Post":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Post/"
    },
    "PostPublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Post/Published"
    },
    "PostUnpublished":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Post/Unpublished"
    },
    "Collaborator":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Collaborator/"
    },
    "Blog":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Blog/"
    },
    "BlogLive":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Blog/Live"
    },
    "Action":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66/Action/"
    },
    "MetaDataIcon":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/Person/66/MetaData/Icon"
    }
}












curl -H 'Accept: application/json' -H 'X-Filter: *,Creator.*,Author.User.*,Author.Source.*' "http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/Published?asc=cId&cId.since=1100"
{"total":"3","lastCId":"1294","limit":"3","offset":"0","PostList":[{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/801","Id":"801","IsModified":"False","IsPublished":"True","WasPublished":"True","CId":"1285","Order":"186.0","AuthorName":"google","Content":"Pražská informační služba – <b>Prague</b> City Tourism chystá na letošní turistickou \nsezonu hned několik projektů. Některé z nich mají oslovit domácí návštěvníky, ...","Meta":"{\"GsearchResultClass\":\"GwebSearch\",\"unescapedUrl\":\"http://www.praguewelcome.cz/\",\"url\":\"http://www.praguewelcome.cz/\",\"visibleUrl\":\"www.praguewelcome.cz\",\"cacheUrl\":\"http://www.google.com/search?q=cache:W5GNv5pfL5MJ:www.praguewelcome.cz\",\"title\":\"Praguewelcome – oficiální turistický průvodce Prahou\",\"titleNoFormatting\":\"Praguewelcome – oficiální turistický průvodce Prahou\",\"content\":\"Pražská informační služba – <b>Prague</b> City Tourism chystá na letošní turistickou \\nsezonu hned několik projektů. Některé z nich mají oslovit domácí návštěvníky, ...\",\"type\":\"web\",\"annotation\":{\"before\":null,\"after\":\"\"}}","Uuid":"5ae3da1dc63845a9b410129840960165","CreatedOn":"3/28/14 11:36 AM","PublishedOn":"3/28/14 11:36 AM","Author":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1","Source":{"href":"//sourcefabric.superdesk.pro/resources/Data/Source/1","Id":"1","IsModifiable":"False","Key":"","Name":"google","Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/xml","Key":"xml"},"URI":{"href":"//sourcefabric.superdesk.pro/www.google.com"}}},"AuthorImage":{"href":"//sourcefabric.superdesk.pro/content/media_archive/thumbnail/original/39.ksmllogo_iso_levea.jpg"},"Blog":{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1","Id":"1"},"Creator":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/66","Id":"66","Active":"True","Cid":"0","EMail":"Janet.Admin@email.addr","FirstName":"Janet","FullName":"Janet Admin","LastName":"Admin","Name":"admin","CreatedOn":"10/14/13 9:22 AM","Type":{"href":"//sourcefabric.superdesk.pro/resources/HR/UserType/standard","Key":"standard"},"MetaDataIcon":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/66/MetaData/Icon"}},"PostVerification":{"href":"//sourcefabric.superdesk.pro/resources/Data/PostVerification/801","Id":"801"},"Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/PostType/normal","Key":"normal"}},{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/462","Id":"462","IsModified":"False","IsPublished":"True","WasPublished":"True","CId":"1290","Order":"187.0","AuthorName":"SMS","Content":"www:This is a duplicate incoming message...","Uuid":"95fd95ac81394da481cd8de1e1315399","CreatedOn":"2/18/14 4:19 PM","PublishedOn":"3/28/14 11:42 AM","Author":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/88","Source":{"href":"//sourcefabric.superdesk.pro/resources/Data/Source/19","Id":"19","IsModifiable":"True","Name":"RightsCon","OriginURI":{"href":"//sourcefabric.superdesk.pro/RightsCon"},"Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/smsblog","Key":"smsblog"},"URI":{"href":"//sourcefabric.superdesk.pro/smsblog/RightsCon"}},"User":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/83","X-Filter":"denied","Id":"83"}},"AuthorPerson":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/83","Id":"83"},"Blog":{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1","Id":"1"},"Creator":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/83","Id":"83","Active":"True","Cid":"0","FirstName":"SMS","FullName":"SMS","Name":"SMS-a825406c8a8e7af2","PhoneNumber":"+420773902784","Uuid":"e27e89ea055746799da549e71c52809a","CreatedOn":"2/18/14 1:18 PM","Type":{"href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms","Key":"sms"},"MetaDataIcon":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/83/MetaData/Icon"}},"Feed":{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Source/19","Id":"19"},"PostVerification":{"href":"//sourcefabric.superdesk.pro/resources/Data/PostVerification/462","Id":"462"},"Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/PostType/normal","Key":"normal"}},{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/459","Id":"459","IsModified":"True","IsPublished":"True","WasPublished":"True","CId":"1294","Order":"188.0","AuthorName":"SMS","Content":"<h3><a href=\"\" target=\"_blank\"></a></h3><div class=\"result-description\"></div><!-- p.result-description tag displays for:> internal link> twitter> google link> google news> google images> flickr> youtube> soundcloud-->Gjm002","Meta":"{\"annotation\":{\"before\":\"This is an SMS.&nbsp;\",\"after\":\"We don't know if it is true.\"}}","Uuid":"d110d863ed274a53b235e9bd9b0f52bf","CreatedOn":"2/18/14 1:22 PM","PublishedOn":"3/28/14 11:42 AM","UpdatedOn":"4/9/14 9:15 AM","Author":{"href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89","Source":{"href":"//sourcefabric.superdesk.pro/resources/Data/Source/19","Id":"19","IsModifiable":"True","Name":"RightsCon","OriginURI":{"href":"//sourcefabric.superdesk.pro/RightsCon"},"Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/smsblog","Key":"smsblog"},"URI":{"href":"//sourcefabric.superdesk.pro/smsblog/RightsCon"}},"User":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84","X-Filter":"denied","Id":"84"}},"AuthorPerson":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/84","Id":"84"},"Blog":{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1","Id":"1"},"Creator":{"href":"//sourcefabric.superdesk.pro/resources/HR/User/84","Id":"84","Active":"True","Cid":"0","FirstName":"SMS","FullName":"SMS","Name":"SMS-77c4fa4b51e11927","PhoneNumber":"+420608577621","Uuid":"4c66a57c428e459da062b6734b9a7a31","CreatedOn":"2/18/14 1:20 PM","Type":{"href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms","Key":"sms"},"MetaDataIcon":{"href":"//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"}},"Feed":{"href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Source/19","Id":"19"},"PostVerification":{"href":"//sourcefabric.superdesk.pro/resources/Data/PostVerification/459","Id":"459"},"Type":{"href":"//sourcefabric.superdesk.pro/resources/Data/PostType/normal","Key":"normal"}}]}mds@tangloid:~$ 

{
"total":"3",
"lastCId":"1294",
"limit":"3",
"offset":"0",
"PostList":
[
{
    "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/801",
    "Id":"801",
    "IsModified":"False",
    "IsPublished":"True",
    "WasPublished":"True",
    "CId":"1285",
    "Order":"186.0",
    "AuthorName":"google",
    "Content":"Pražská informační služba – <b>Prague</b> City Tourism chystá na letošní turistickou \nsezonu hned několik projektů. Některé z nich mají oslovit domácí návštěvníky, ...",
    "Meta":"{\"GsearchResultClass\":\"GwebSearch\",\"unescapedUrl\":\"http://www.praguewelcome.cz/\",\"url\":\"http://www.praguewelcome.cz/\",\"visibleUrl\":\"www.praguewelcome.cz\",\"cacheUrl\":\"http://www.google.com/search?q=cache:W5GNv5pfL5MJ:www.praguewelcome.cz\",\"title\":\"Praguewelcome – oficiální turistický průvodce Prahou\",\"titleNoFormatting\":\"Praguewelcome – oficiální turistický průvodce Prahou\",\"content\":\"Pražská informační služba – <b>Prague</b> City Tourism chystá na letošní turistickou \\nsezonu hned několik projektů. Některé z nich mají oslovit domácí návštěvníky, ...\",\"type\":\"web\",\"annotation\":{\"before\":null,\"after\":\"\"}}",
    "Uuid":"5ae3da1dc63845a9b410129840960165",
    "CreatedOn":"3/28/14 11:36 AM",
    "PublishedOn":"3/28/14 11:36 AM",
    "Author":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/1",
        "Source":
        {
            "href":"//sourcefabric.superdesk.pro/resources/Data/Source/1",
            "Id":"1",
            "IsModifiable":"False",
            "Key":"",
            "Name":"google",
            "Type":
            {
                "href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/xml",
                "Key":"xml"
            },
            "URI":
            {
                "href":"//sourcefabric.superdesk.pro/www.google.com"
            }
        }
    },
    "AuthorImage":
    {
        "href":"//sourcefabric.superdesk.pro/content/media_archive/thumbnail/original/39.ksmllogo_iso_levea.jpg"
    },
    "Blog":
    {
        "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1",
        "Id":"1"
    },
    "Creator":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/66",
        "Id":"66",
        "Active":"True",
        "Cid":"0",
        "EMail":"Janet.Admin@email.addr",
        "FirstName":"Janet",
        "FullName":"Janet Admin",
        "LastName":"Admin",
        "Name":"admin",
        "CreatedOn":"10/14/13 9:22 AM",
        "Type":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/UserType/standard",
            "Key":"standard"
        },
        "MetaDataIcon":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/Person/66/MetaData/Icon"
        }
    },
    "PostVerification":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/PostVerification/801",
        "Id":"801"
    },
    "Type":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/PostType/normal",
        "Key":"normal"
    }
},
{
    "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/462",
    "Id":"462",
    "IsModified":"False",
    "IsPublished":"True",
    "WasPublished":"True",
    "CId":"1290",
    "Order":"187.0",
    "AuthorName":"SMS",
    "Content":"www:This is a duplicate incoming message...",
    "Uuid":"95fd95ac81394da481cd8de1e1315399",
    "CreatedOn":"2/18/14 4:19 PM",
    "PublishedOn":"3/28/14 11:42 AM",
    "Author":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/88",
        "Source":
        {
            "href":"//sourcefabric.superdesk.pro/resources/Data/Source/19",
            "Id":"19",
            "IsModifiable":"True",
            "Name":"RightsCon",
            "OriginURI":
            {
                "href":"//sourcefabric.superdesk.pro/RightsCon"
            },
            "Type":
            {
                "href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/smsblog",
                "Key":"smsblog"
            },
            "URI":
            {
                "href":"//sourcefabric.superdesk.pro/smsblog/RightsCon"
            }
        },
        "User":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/User/83",
            "X-Filter":"denied",
            "Id":"83"
        }
    },
    "AuthorPerson":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/Person/83",
        "Id":"83"
    },
    "Blog":
    {
        "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1",
        "Id":"1"
    },
    "Creator":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/83",
        "Id":"83",
        "Active":"True",
        "Cid":"0",
        "FirstName":"SMS",
        "FullName":"SMS",
        "Name":"SMS-a825406c8a8e7af2",
        "PhoneNumber":"+420773902784",
        "Uuid":"e27e89ea055746799da549e71c52809a",
        "CreatedOn":"2/18/14 1:18 PM",
        "Type":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms",
            "Key":"sms"
        },
        "MetaDataIcon":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/Person/83/MetaData/Icon"
        }
    },
    "Feed":
    {
        "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Source/19",
        "Id":"19"
    },
    "PostVerification":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/PostVerification/462",
        "Id":"462"
    },
    "Type":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/PostType/normal",
        "Key":"normal"
    }
},
{
    "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/459",
    "Id":"459",
    "IsModified":"True",
    "IsPublished":"True",
    "WasPublished":"True",
    "CId":"1294",
    "Order":"188.0",
    "AuthorName":"SMS",
    "Content":"<h3><a href=\"\" target=\"_blank\"></a></h3><div class=\"result-description\"></div><!-- p.result-description tag displays for:> internal link> twitter> google link> google news> google images> flickr> youtube> soundcloud-->Gjm002",
    "Meta":"{\"annotation\":{\"before\":\"This is an SMS.&nbsp;\",\"after\":\"We don't know if it is true.\"}}",
    "Uuid":"d110d863ed274a53b235e9bd9b0f52bf",
    "CreatedOn":"2/18/14 1:22 PM",
    "PublishedOn":"3/28/14 11:42 AM",
    "UpdatedOn":"4/9/14 9:15 AM",
    "Author":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/Collaborator/89",
        "Source":
        {
            "href":"//sourcefabric.superdesk.pro/resources/Data/Source/19",
            "Id":"19",
            "IsModifiable":"True",
            "Name":"RightsCon",
            "OriginURI":
            {
                "href":"//sourcefabric.superdesk.pro/RightsCon"
            },
            "Type":
            {
                "href":"//sourcefabric.superdesk.pro/resources/Data/SourceType/smsblog",
                "Key":"smsblog"
            },
            "URI":
            {
                "href":"//sourcefabric.superdesk.pro/smsblog/RightsCon"
            }
        },
        "User":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/User/84",
            "X-Filter":"denied",
            "Id":"84"
        }
    },
    "AuthorPerson":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/Person/84",
        "Id":"84"
    },
    "Blog":
    {
        "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1",
        "Id":"1"
    },
    "Creator":
    {
        "href":"//sourcefabric.superdesk.pro/resources/HR/User/84",
        "Id":"84",
        "Active":"True",
        "Cid":"0",
        "FirstName":"SMS",
        "FullName":"SMS",
        "Name":"SMS-77c4fa4b51e11927",
        "PhoneNumber":"+420608577621",
        "Uuid":"4c66a57c428e459da062b6734b9a7a31",
        "CreatedOn":"2/18/14 1:20 PM",
        "Type":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/UserType/sms",
            "Key":"sms"
        },
        "MetaDataIcon":
        {
            "href":"//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon"
        }
    },
    "Feed":
    {
        "href":"//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Source/19",
        "Id":"19"
    },
    "PostVerification":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/PostVerification/459",
        "Id":"459"
    },
    "Type":
    {
        "href":"//sourcefabric.superdesk.pro/resources/Data/PostType/normal",
        "Key":"normal"
    }
}
]
}

'''

lb_blog_post_published_list = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/Published',
    'lb_content': {
        'PostList': [{'href':'//sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/459'}, ...]
    },
    'cd_data': 'list of published reports set to the coverage; have to find out how to only display unseen reports',
}

lb_blog_post {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/LiveDesk/Blog/1/Post/459',
    'lb_content': {
        'Id': '1',
        'CId': '1294',
        'AuthorName': 'SMS',
        'Content': '<h3><a href="" target="_blank"></a></h3><div class="result-description"></div><!-- p.result-description tag displays for:> internal link> twitter> google link> google news> google images> flickr> youtube> soundcloud-->Gjm002',
        'Meta': '{"annotation":{"before":"This is an SMS.&nbsp;","after":"We don\'t know if it is true."}}',
        'Author': {'href':'//sourcefabric.superdesk.pro/resources/Data/Collaborator/89','Id':'89'},
        'AuthorPerson':{'href':'//sourcefabric.superdesk.pro/resources/HR/Person/84','Id':'84'},
    },
    'cd_data': 'taken from report data',
}

lb_person = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/HR/Person/84',
    'lb_content': {
        'Id': '84',
        'FirstName': 'SMS',
        'FullName': 'SMS',
        'PhoneNumber': '+420608577621',
        'MetaDataIcon': {'href':'//sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon'},
    },
    'cd_data': 'have to find out what is required',
}

lb_meta_data_icon = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/HR/Person/84/MetaData/Icon',
    'lb_content': None,
    'cd_data': 'return status code 400',
}

lb_collaborator = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/Data/Collaborator/89',
    'lb_content': {
        'Id': '89',
        'Name': 'SMS',
        'User': {
            'href': '//sourcefabric.superdesk.pro/resources/HR/User/84',
            'Id': '84',
        },
    },
    'cd_data': 'have to find out what is required',
}

lb_user = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/HR/User/84',
    'lb_content': {
        'Id': '84',
        'Active': True,
        'Cid': '0',
        'FirstName': 'SMS',
        'FullName': 'SMS',
        'PhoneNumber': '+420608577621',
    },
    'cd_data': 'have to find out what is required',
}

lb_user = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/HR/User/3',
    'lb_content': {
        'Id': '3',
        'Active': False,
        'Cid': '0',
        'EMail': 'Andrew.Reporter@email.addr',
        'FirstName': 'Andrew',
        'FullName': 'Andrew Reporter',
        'LastName': 'Reporter',
    },
    'cd_data': 'have to find out what is required',
}

lb_verification_status_list = {
    'lb_link': 'http://sourcefabric.superdesk.pro/resources/Data/VerificationStatus/',
    'lb_content': {
        'VerificationStatusList': [{'href':'//sourcefabric.superdesk.pro/resources/Data/VerificationStatus/nostatus'}, ...]
    },
    'cd_data': 'we will see if we can pass anything like this on',
}


