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

import os, sys, datetime, logging, json
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

def get_tweet(report_id):
    try:
        return holder.provide_report(report_id)
    except:
        return None

def process_new_tweet(tweet_id, tweet, feed_filter, endpoint_id, client_ip):

    feed_type = get_conf('feed_type')
    report_id = gen_id(feed_type, tweet_id)
    if not report_id:
        return (False, 'wrong tweet_id')

    session_id = report_id

    parent_id = None
    if ('in_reply_to_status_id' in tweet) and tweet['in_reply_to_status_id']:
        parent_id = tweet['in_reply_to_status_id']

    parent_tweet = get_tweet(gen_id(feed_type, parent_id)) if parent_id else None
    if parent_tweet and ('session' in parent_tweet):
        session_id = parent_tweet['session']

    report = {
        'report_id': report_id,
        'parent_id': parent_id,
        'client_ip': client_ip,
        'feed_type': feed_type,
        'channels': [{'type': get_conf('channel_type'), 'value': endpoint_id, 'filter': feed_filter}],
        'publishers': [{'type': get_conf('publisher_type'), 'value': get_conf('feed_publisher')}],
        'session': session_id,
        'proto': True,
        'original': tweet
    }
    try:
        if 'created_at' in tweet:
            report['produced'] = tweet['created_at']
        else:
            report['produced'] = None
        if not report['produced']:
            report['produced'] = datetime.datetime.now()
        report['language'] = tweet['lang']

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

        report_entities = tweet['entities']
        report_text = tweet['text']
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
            report['texts'] = [report_text]

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
                        if (size_spec in one_link['sizes']) and one_link['sizes'][size_spec]:
                            one_size = one_link['sizes'][size_spec]
                            if ('resize' not in one_size) or ('w' not in one_size) or ('h' not in one_size):
                                continue
                            if one_size['resize'] != 'fit':
                                continue
                            one_width = one_size['w']
                            one_height = one_size['h']
                            break
                    rep_media.append({'link': one_link['expanded_url'], 'width': one_width, 'height': one_height})
                report['media'] = rep_media

            rep_citizens = []
            if ('user_mentions' in report_entities) and report_entities['user_mentions']:
                for one_citz in report_entities['user_mentions']:
                    mentioned_citz = {'user_id': one_citz['id_str'], 'user_name': one_citz['screen_name']}
                    rep_citizens.append({'authority': 'twitter', 'identifiers': mentioned_citz})
            report['citizens'] = rep_citizens

        one_author_ids = [{'type':'user_id', 'value':tweet['user']['id_str']}, {'type':'user_name', 'value':tweet['user']['screen_name']}]
        rep_authors = [{'authority': 'twitter', 'identifiers': one_author_ids}]
        if ('contributors' in tweet) and tweet['contributors']:
            for one_cont in tweet['contributors']:
                one_cont_ids = [{'type':'user_id', 'value':one_cont['id_str']}, {'type':'user_name', 'value':one_cont['screen_name']}]
                rep_authors.append({'authority': 'twitter', 'identifiers': one_cont_ids})
        report['authors'] = rep_authors

    except Exception as exc:
        sys.stderr.write(str(exc) + '\n')
        return (False, 'wrong tweet structure')

    holder.save_report(report)

    return (True,)


twt_take = Blueprint('twt_take', __name__)

@twt_take.route('/newstwister/tweets/<tweet_id>', defaults={}, methods=['POST'], strict_slashes=False)
def take_twt(tweet_id):
    client_ip = get_client_ip()

    allowed_ips = get_conf('allowed_ips')
    if allowed_ips and ('*' not in allowed_ips):
        if not client_ip in allowed_ips:
            return ('Client not allowed\n\n', 403,)

    try:
        json_data = request.get_json(True, False, False)
    except:
        json_data = None

    if not json_data:
        return ('Data not provided', 404,)
    for part in ['filter', 'tweet', 'endpoint']:
        if (part not in json_data) or (not json_data[part]):
            return ('No ' + str(part) + ' provided', 404,)

    tweet = json_data['tweet']
    feed_filter = json_data['filter']
    endpoint = json_data['endpoint']

    try:
        endpoint_id = endpoint['endpoint_id']
    except:
        return ('endpoint[endpoint_id] not provided', 404,)

    feed_type = get_conf('feed_type')

    # check if the tweet is a new tweet, already saved tweet, a retweet, or a retweet on an already saved tweet

    # for a retweet, set endorsers (and may be comments if a new one)
    retweeted_report = None
    retweeted_id = None
    retweeted_tweet = None
    try:
        current_sub = tweet
        while current_sub['retweeted_status']:
            current_sub = current_sub['retweeted_status']
            retweeted_tweet = current_sub
            retweeted_id = retweeted_tweet['id_str']
    except:
        retweeted_id = None
        retweeted_tweet = None

    # if tweet already saved, add publishers, channels part
    main_report_id = gen_id(feed_type, (retweeted_id if retweeted_id else tweet_id))
    tweet_report = get_tweet(main_report_id)

    if tweet_report:
        main_report_id = tweet_report['report_id']
        holder.add_channels(main_report_id, [{'type': get_conf('channel_type'), 'value': endpoint_id, 'filter': feed_filter}])
        holder.add_publishers(main_report_id, [{'type': get_conf('publisher_type'), 'value': get_conf('feed_publisher')}])
    else:
        main_tweet_id = retweeted_id if retweeted_id else tweet_id
        main_tweet = retweeted_tweet if retweeted_tweet else tweet
        res = process_new_tweet(main_tweet_id, main_tweet, feed_filter, endpoint_id, client_ip)
        if (not res) or (not res[0]):
            return (res[1], 404,)

    # for a retweet, set endorsers for the original tweet
    if retweeted_id:
        try:
            endorser_ids = [{'type':'user_id', 'value':tweet['user']['id_str']}, {'type':'user_name', 'value':tweet['user']['screen_name']}]
            rep_endorser = [{'authority': 'twitter', 'identifiers': endorser_ids}]
            holder.add_endorsers(main_report_id, [rep_endorser])
        except:
            return ('can not add endorsers', 404,)

    return ('Tweet received\n\n', 200,)
