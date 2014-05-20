#!/usr/bin/env python
#
# Citizen Desk
#
'''
If the tweet is already saved, only add the feed_spec, publishers and channels part.
Retweets: They probably should be put in as endorsing. And if they create a new text, put that text in as a comment.

# basic info
_id/report_id: tweet_id
parent_id: tweet: in_reply_to_status_id
client_ip: newstwister_ip
feed_type: tweet
produced:  tweet: created_at
created: None # datetime.now().isoformat()
modified: None
session: tweet: retweeted_status: id_str or tweet_id; for request count limits, ids of conversation starts should only be searched on user actions
proto: True
language: tweet: lang
sensitive: tweet: possibly_sensitive

# status
verification: None
importance: None
relevance: None
checks: []
assignments: []

# citizens
channels: [{type:twitter, value: endpoint: endpoint_id}]
#publishers: [{type:twitter, value:twitter stream}]
publisher: 'twitter'
authors: [{'authority': 'twitter', 'identifiers': [{type:id, value:tweet:user:id_str}, {type:screen_name, value:tweet:user:screen_name}]}]
recipients: []
endorsers: [] # users that retweet

# content
original: tweet
geolocations: tweet: coordinates [(lon, lat)] or tweet: geo (lat, lon)
place_names: tweet: place
timeline: []
time_names: []
citizens_mentioned: [{'authority': 'twitter', 'identifiers': [{type:id, value:tweet:entities:user_mentions:id_str}, {type:screen_name, value:tweet:entities:user_mentions:screen_name}]}]
subjects: []
media: [tweet: entities: media: {'type':type, 'url':media_url where resize=='fit'}]
texts: [{tweet: text}] plus replace links to their original values
links: [tweet: entities: urls: expanded_url]
notices_inner: []
notices_outer: []
comments: [{}] # retweets
tags: [tweet: entities: hashtags: text]

# clients
viewed: []
discarded: []
'''

SOURCE_START = 'https://twitter.com/'
SOURCE_MIDDLE = '/status/'
SOURCE_END = '/'

import os, sys, datetime, json
from citizendesk.ingest.twt.connect import get_conf, gen_id, get_tweet

def _get_expanded_text(original_tweet):
    expanded_text = ''

    report_entities = original_tweet['entities']
    report_text = original_tweet['text']
    if report_text:
        if report_entities:
            replace_set = {}
            # change links to original links
            all_url_sets = []
            for link_entity_type in ['urls', 'media']:
                if (link_entity_type in report_entities) and report_entities[link_entity_type]:
                    all_url_sets.append(report_entities[link_entity_type])
            for one_url_set in all_url_sets:
                if one_url_set:
                    for one_url in one_url_set:
                        replace_set[one_url['indices'][0]] = {'indices': one_url['indices'], 'url': one_url['expanded_url']}
            for key in sorted(replace_set.keys(), reverse=True):
                link_data = replace_set[key]
                report_text = report_text[:link_data['indices'][0]] + link_data['url'] + report_text[link_data['indices'][1]:]
        expanded_text = report_text

    return expanded_text

def _take_twt_user_names(citizen_alias_lists):
    names = []

    # we use screen_names all here now
    for one_set in citizen_alias_lists:
        for one_alias in one_set:
            if one_alias['authority'] != 'twitter':
                continue
            for one_alias_spec in one_alias['identifiers']:
                if one_alias_spec['type'] == 'user_name':
                    names.append(one_alias_spec['value'].lower())

    return names

def find_search_reason(criteria, expanded_text, authors, endorsers, recipients):
    reasons_track = []
    reasons_follow = []

    expanded_text = expanded_text.lower()

    tweet_authors = _take_twt_user_names([authors, endorsers])
    tweet_recipients = _take_twt_user_names([recipients])

    if ('query' in criteria) and (type(criteria['query']) is dict):

        if 'contains' in criteria['query']:
            term_parts = criteria['query']['contains']
            if type(term_parts) not in [list, tuple]:
                term_parts = []
            for one_term in term_parts:
                one_term = one_term.strip()
                if not one_term:
                    continue
                if str(one_term).lower() in expanded_text:
                    reasons_track.append(one_term)

        if 'from' in criteria['query']:
            from_part = criteria['query']['from']
            if from_part:
                if str(from_part).lower() in tweet_authors:
                    reasons_follow.append(from_part)

        if 'to' in criteria['query']:
            to_part = criteria['query']['to']
            if to_part:
                if str(to_part).lower() in tweet_recipients:
                    reasons_follow.append(to_part)

    return {'track': reasons_track, 'follow': reasons_follow}

def find_stream_reason(criteria, expanded_text, authors, endorsers, recipients):
    reasons_track = []
    reasons_follow = []

    expanded_text = expanded_text.lower()

    term_parts = []
    if 'track' in criteria:
        term_parts = criteria['track']
        if type(term_parts) not in [list, tuple]:
            term_parts = []

    for term_tuple in term_parts:
        term_tuple = term_tuple.strip()
        if not term_tuple:
            continue
        tuple_present = True
        for one_term in term_tuple.split(' '):
            if not one_term:
                continue
            if str(one_term).lower() not in expanded_text:
                tuple_present = False
                break
        if tuple_present:
            reasons_track.append(term_tuple)

    tweet_borders = _take_twt_user_names([authors, endorsers, recipients])

    follow_parts = []
    if 'follow' in criteria:
        follow_parts = criteria['follow']
        if type(follow_parts) not in [list, tuple]:
            follow_parts = []

    for one_follow in follow_parts:
        if str(one_follow).lower() in tweet_borders:
            reasons_follow.append(one_follow)

    return {'track': reasons_track, 'follow': reasons_follow}

def process_new_tweet(holder, tweet_id, tweet, channel_type, endpoint_id, request_id, feed_filter, endorsers, client_ip):

    feed_type = get_conf('feed_type')
    report_id = gen_id(feed_type, tweet_id)
    if not report_id:
        return (False, 'wrong tweet_id')

    session_id = report_id

    parent_id = None
    if ('in_reply_to_status_id_str' in tweet) and tweet['in_reply_to_status_id_str']:
        parent_id = tweet['in_reply_to_status_id_str']
    if parent_id:
        session_id = gen_id(feed_type, parent_id)

    parent_tweet = get_tweet(gen_id(feed_type, parent_id)) if parent_id else None
    proto = True
    pinned_id = None
    assignments = []

    if parent_tweet:
        if 'session' in parent_tweet:
            session_id = parent_tweet['session']
        if 'proto' in parent_tweet:
            proto = parent_tweet['proto']
        if 'pinned_id' in parent_tweet:
            pinned_id = parent_tweet['pinned_id']
        if 'assignments' in parent_tweet:
            assignments = parent_tweet['assignments']

    report = {
        'report_id': report_id,
        'parent_id': parent_id,
        'client_ip': client_ip,
        'feed_type': feed_type,
        'publisher': get_conf('publisher'),
        'session': session_id,
        'proto': proto,
        'pinned_id': pinned_id,
        'assignments': assignments,
        'original': tweet,
        'endorsers': endorsers,
        'recipients': [],
        'sources': []
    }

    expanded_text = ''
    try:
        if 'created_at' in tweet:
            try:
                report['produced'] = datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            except:
                report['produced'] = None
        else:
            report['produced'] = None
        if not report['produced']:
            report['produced'] = datetime.datetime.now()
        report['language'] = tweet['lang']

        if tweet_id and ('user' in tweet) and (type(tweet['user']) is dict) and ('screen_name' in tweet['user']):
            report['sources'] = [SOURCE_START + str(tweet['user']['screen_name']) + SOURCE_MIDDLE + str(tweet_id) + SOURCE_END]

        if 'possibly_sensitive' in tweet:
            report['sensitive'] = tweet['possibly_sensitive']

        if ('place' in tweet) and tweet['place']:
            if tweet['place']['full_name']:
                place_name = tweet['place']['full_name']
                if tweet['place']['country_code']:
                    place_name += ', ' + tweet['place']['country_code']
                report['place_names'] = [place_name]

        if ('coordinates' in tweet) and tweet['coordinates'] and tweet['coordinates']['coordinates'] and tweet['coordinates']['type']:
            if 'point' == tweet['coordinates']['type'].lower():
                coordinates = tweet['coordinates']['coordinates']
                report['geolocations'] = [{'lon': coordinates[0], 'lat': coordinates[1]}]

        expanded_text = _get_expanded_text(tweet)
        report['texts'] = [{'original': expanded_text, 'transcript': None}]

        report_entities = tweet['entities']
        if report_entities:
            if ('hashtags' in report_entities) and report_entities['hashtags']:
                rep_tags = []
                for one_tag in report_entities['hashtags']:
                    rep_tags.append(one_tag['text'])
                report['tags'] = rep_tags

            if ('urls' in report_entities) and report_entities['urls']:
                rep_links = []
                for one_link in report_entities['urls']:
                    rep_links.append(one_link['expanded_url'])
                report['links'] = rep_links

            if ('media' in report_entities) and report_entities['media']:
                rep_media = []
                for one_media in report_entities['media']:
                    one_width = None
                    one_height = None
                    for size_spec in ['large', 'medium', 'small']:
                        if (size_spec in one_media['sizes']) and one_media['sizes'][size_spec]:
                            one_size = one_media['sizes'][size_spec]
                            if ('resize' not in one_size) or ('w' not in one_size) or ('h' not in one_size):
                                continue
                            if one_size['resize'] != 'fit':
                                continue
                            one_width = one_size['w']
                            one_height = one_size['h']
                            break
                    rep_media.append({
                        'link': one_media['media_url'],
                        'link_ssl': one_media['media_url_https'],
                        'width': one_width,
                        'height': one_height
                    })
                report['media'] = rep_media

            rep_citizens = []
            if ('user_mentions' in report_entities) and report_entities['user_mentions']:
                for one_citz in report_entities['user_mentions']:
                    mentioned_citz = [
                        {'type': 'user_id', 'value': one_citz['id_str']},
                        {'type': 'user_name', 'value': one_citz['screen_name']}
                    ]
                    rep_citizens.append({'authority': 'twitter', 'identifiers': mentioned_citz})
            report['citizens_mentioned'] = rep_citizens

        one_author_ids = [{'type':'user_id', 'value':tweet['user']['id_str']}, {'type':'user_name', 'value':tweet['user']['screen_name']}]
        rep_authors = [{'authority': 'twitter', 'identifiers': one_author_ids}]
        if ('contributors' in tweet) and tweet['contributors']:
            for one_cont in tweet['contributors']:
                one_cont_ids = [{'type':'user_id', 'value':one_cont['id_str']}, {'type':'user_name', 'value':one_cont['screen_name']}]
                rep_authors.append({'authority': 'twitter', 'identifiers': one_cont_ids})
        report['authors'] = rep_authors

        recipient_id = None
        recipient_name = None
        if 'in_reply_to_user_id_str' in tweet:
            recipient_id = tweet['in_reply_to_user_id_str']
        if 'in_reply_to_screen_name' in tweet:
            recipient_name = tweet['in_reply_to_screen_name']
        if recipient_id and recipient_name:
            one_recp_ids = [{'type':'user_id', 'value':recipient_id}, {'type':'user_name', 'value':recipient_name}]
            report['recipients'].append({'authority': 'twitter', 'identifiers': one_recp_ids})

    except Exception as exc:
        sys.stderr.write(str(exc) + '\n')
        return (False, 'wrong tweet structure')

    try:
        one_channel = {'type': channel_type, 'value': endpoint_id, 'request': request_id, 'filter': feed_filter}

        reasons = {}
        if 'stream' == channel_type:
            reasons = find_stream_reason(feed_filter, expanded_text, report['authors'], endorsers, report['recipients'])
        if 'search' == channel_type:
            reasons = find_search_reason(feed_filter, expanded_text, report['authors'], endorsers, report['recipients'])
        one_channel['reasons'] = reasons

        report['channels'] = [one_channel]

    except Exception as exc:
        sys.stderr.write(str(exc) + '\n')
        return (False, 'can not extract the reasons')

    res = holder.save_report(report)
    if not res:
        return (False, 'can not save the report')

    return (True,)

def do_post(holder, tweet_id, tweet, channel_type, endpoint, request_id, feed_filter, client_ip):
    try:
        endpoint_id = endpoint['endpoint_id']
    except:
        return (False, 'endpoint[endpoint_id] not provided',)

    feed_type = get_conf('feed_type')

    # check if the tweet is a new tweet, already saved tweet, a retweet, or a retweet on an already saved tweet

    # for a retweet, set endorsers (and may be comments if a new one)
    retweeted_report = None
    retweeted_id = None
    retweeted_tweet = None
    try:
        current_sub = tweet
        while ('retweeted_status' in current_sub) and current_sub['retweeted_status']:
            current_sub = current_sub['retweeted_status']
            retweeted_tweet = current_sub
            retweeted_id = retweeted_tweet['id_str']
    except:
        retweeted_id = None
        retweeted_tweet = None

    # we need to have endorsers extracted early for extracting the reasons
    report_endorsers = []
    if retweeted_id:
        try:
            endorser_ids = [{'type':'user_id', 'value':tweet['user']['id_str']}, {'type':'user_name', 'value':tweet['user']['screen_name']}]
            report_endorsers = [{'authority': 'twitter', 'identifiers': endorser_ids}]
        except:
            return (False, 'can not create endorsers',)

    # if tweet already saved, add channels part
    main_report_id = gen_id(feed_type, (retweeted_id if retweeted_id else tweet_id))
    tweet_report = get_tweet(main_report_id)

    if tweet_report:
        main_report_id = tweet_report['report_id']
        one_channel = {'type': channel_type, 'value': endpoint_id, 'request': request_id, 'filter': feed_filter, 'reasons': {}}

        try:
            expanded_text = _get_expanded_text(tweet_report['original'])

            reasons = {}
            if 'stream' == channel_type:
                reasons = find_stream_reason(feed_filter, expanded_text, tweet_report['authors'], report_endorsers, tweet_report['recipients'])
            if 'search' == channel_type:
                reasons = find_search_reason(feed_filter, expanded_text, tweet_report['authors'], report_endorsers, tweet_report['recipients'])
            one_channel['reasons'] = reasons
        except Exception as exc:
            sys.stderr.write(str(exc) + '\n')
            return (False, 'can extract the reasons')

        holder.add_channels(main_report_id, [one_channel])

        # for a retweet, set endorsers for the original tweet
        if retweeted_id:
            try:
                holder.add_endorsers(main_report_id, report_endorsers)
            except:
                return (False, 'can not add endorsers',)

    else:
        main_tweet_id = retweeted_id if retweeted_id else tweet_id
        main_tweet = retweeted_tweet if retweeted_tweet else tweet
        res = process_new_tweet(holder, main_tweet_id, main_tweet, channel_type, endpoint_id, request_id, feed_filter, report_endorsers, client_ip)
        if not res[0]:
            return (False, res[1])

    return (True,)

