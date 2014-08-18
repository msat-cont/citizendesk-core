#!/usr/bin/env mongo

conn = new Mongo();
db = conn.getDB("citizendesk");


db['reports'].ensureIndex({'report_id': -1});
db['reports'].ensureIndex({'original_id': 1});
db['reports'].ensureIndex({'proto': 1});
db['reports'].ensureIndex({'channels': 1});
db['reports'].ensureIndex({'feed_type': 1});
db['reports'].ensureIndex({'authors': 1});
db['reports'].ensureIndex({'recipients': 1});

db['reports'].ensureIndex({'created': -1});
db['reports'].ensureIndex({'produced': -1});
db['reports'].ensureIndex({'updated': -1});
db['reports'].ensureIndex({'_created': -1});
db['reports'].ensureIndex({'_produced': -1});
db['reports'].ensureIndex({'_updated': -1});


db['citizen_aliases'].ensureIndex({'authority': -1});
db['citizen_aliases'].ensureIndex({'identifiers': -1});



