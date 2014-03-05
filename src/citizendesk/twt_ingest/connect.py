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
feed_spec: [{'filter': filter}]
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
publishers: [{type:twitter, value:twitter stream}]
authors: [{'authority': 'twitter', 'identifiers': [{type:id, value:tweet:user:id_str}, {type:screen_name, value:tweet:user:screen_name}]}]
endorsers: [] # users that retweet

# content
original: tweet
geolocations: tweet: coordinates [(lon, lat)] or tweet: geo (lat, lon)
place_names: tweet: place
timeline: []
time_names: []
citizens: [{'authority': 'twitter', 'identifiers': [{type:id, value:tweet:entities:user_mentions:id_str}, {type:screen_name, value:tweet:entities:user_mentions:screen_name}]}]
subjects: []
media: [tweet: entities: media: {'type':type, 'url':media_url where resize=='fit'}]
texts: [tweet: text] plus replace links to their original values
links: [tweet: entities: urls: expanded_url]
transcripts: []
notices_inner: []
notices_outer: []
comments: [{}] # retweets
tags: [tweet: entities: hashtags: text]

# clients
viewed: []
discarded: []
'''

import os, sys, datetime, logging
try:
    from flask import Blueprint, request
except:
    logging.error('Flask module is not avaliable\n')
    os._exit(1)

from citizendesk.reporting.utils import get_client_ip
from citizendesk.reporting.holder import ReportHolder
holder = ReportHolder()

def get_conf(name):
    config = {'feed_type':'tweet', 'feed_publisher':'twitter stream', 'channel_type': 'twitter', 'publisher_type': 'twitter'}
    config['allowed_ips'] = '127.0.0.1'

    if name in config:
        return config[name]
    return None

def gen_id(feed_type, id_str):
    try:
        id_value = '' + feed_type + ':' + id_str
        return id_value
    except:
        return None

twt_take = Blueprint('twt_take', __name__)

@twt_take.route('/newstwister/tweets/<tweet_id>', defaults={}, methods=['POST'], strict_slashes=False)
def take_twt(tweet_id):
    client_ip = get_client_ip()

    allowed_ips = get_conf('allowed_ips')
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            return (403, 'Client not allowed\n\n')

    try:
        json_data = request.get_json(True, False, False)
    except:
        json_data = None

    if not json_data:
        return (404, 'Data not provided')
    for part in ['filter', 'tweet', 'endpoint']:
        if (part not in json_data) or (not json_data[part]):
            return (404, 'No ' + str(part) + ' provided')

    tweet = json_data['tweet']
    feed_filter = json_data['filter']
    endpoint = json_data['endpoint']

    try:
        endpoint_id = endpoint['endpoint_id']
    except:
        return (404, 'endpoint[endpoint_id] not provided')

    # if tweet already saved, add feed_spec, publishers, channels part
    # below is the setting of a new tweet, i.e. not a retweet
    # otherwise set comments, endorsers for a retweet

    feed_type = get_conf('feed_type')
    report_id = gen_id(feed_type, tweet_id)
    if not report_id:
        return (404, 'wrong tweet_id')

    session_id = report_id

    parent_id = None
    if ('in_reply_to_status_id' in tweet) and tweet['in_reply_to_status_id']:
        parent_id = tweet['in_reply_to_status_id']

    parent_tweet = get_tweet(report_id) if parent_id else None
    if parent_tweet and ('session' in parent_tweet):
        session_id = parent_tweet['session']

    report = {
        'report_id': report_id,
        'parent_id': parent_id,
        'client_ip': client_ip,
        'feed_type': feed_type,
        'feed_spec': [{'filter': feed_filter}],
        'channels': [{'type': get_conf('channel_type'), 'value': endpoint_id}],
        'publishers': [{'type': get_conf('publisher_type'), 'value': get_conf('feed_publisher')}],
        'session': session_id,
        'proto': True,
        'original': tweet
    }
    try:
        report['produced'] = tweet['created_at']
        if not report['produced']:
            report['produced'] = datetime.datetime.now()
        report['language'] = tweet['lang']
        report['sensitive'] = tweet['possibly_sensitive']

        if tweet['place']:
            if tweet['place']['full_name']:
                place_name = tweet['place']['full_name']
                if tweet['place']['country_code']:
                    place_name += ', ' + tweet['place']['country_code']
                report['place_names'] = [place_name]

        if tweet['coordinates'] and tweet['coordinates']['coordinates'] and tweet['coordinates']['type']:
            if 'point' == tweet['coordinates']['type'].lower():
                coordinates = tweet['coordinates']['coordinates']
                report['geolocations'] = [{'lon': coordinates[0], 'lat': coordinates[1]}]

        report_entities = tweet['entities']
        report_text = tweet['text']
        if report_text:
            if report_entities:
                replace_set = {}
                # replace links to original links
                for one_url_set in [report_entities['urls'], report_entities['media']]:
                    if one_url_set:
                        for one_url in one_url_set['urls']:
                            replace_set[one_url['indices'][0]] = {'indices': one_url['indices'], 'url': one_url['expanded_url']}
                for key in sorted(replace_set.keys(), reverse=True):
                    link_data = replace_set[key]
                    report_text = report_text[:link_data['indices']] + link_data['url'] + report_text[link_data['indices']:]
            report['texts'] = [report_text]

        if report_entities:
            if report_entities['hashtags']:
                rep_tags = []
                for one_tag in report_entities['hashtags']:
                    rep_tags.append(one_tag['text'])
                report['tags'] = rep_tags

            if report_entities['urls']:
                rep_links = []
                for one_link in report_entities['urls']:
                    rep_links.append(one_link['expanded_url'])
                report['links'] = rep_links

        '''these yet to do:
            report['media'] = [tweet['tweet: entities: media: {"type":type, "url":media_url where resize=="fit"}']]

        report['authors'] = [{'authority': 'twitter', 'identifiers': '[{type:id, value:tweet:user:id_str}, {type:screen_name, value:tweet:user:screen_name}]'}]
        #report['authors'] = [{'type':'twitter', 'value':twitter_user_id}]
        report['citizens'] = [{'authority': 'twitter', 'identifiers': '[{type:id, value:tweet:entities:user_mentions:id_str}, {type:screen_name, value:tweet:entities:user_mentions:screen_name}]'}]
        '''

    except:
        return (404, 'wrong tweet structure')

    '''
    session_look_spec = {'channel': {'type':channels[0]['type']}, 'author':authors[0]}
    force_new_session = holder.get_force_new_session(session_look_spec)
    if force_new_session:
        holder.clear_force_new_session(session_look_spec, True)
    else:
        last_report = holder.find_last_session({'channels':channels[0], 'authors':authors[0]})
        if last_report:
            if within_session(last_report['received'], received):
                session = last_report['session']
                new_session = False
    '''

    holder.save_report(report)

    return (200, 'Tweet received\n\n')

