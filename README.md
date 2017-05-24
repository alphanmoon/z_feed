# z_feed
Just another tweeting python bot with hashtags inserting smart machine


* reads choosen news feeds, 
* makes title parsing,
* sets keywords in titles by spoting NOUNs
* inserts hashtags afore keywords
* builds posts and tweets 'em
* waits for fresh news (used news links are packed in json) 

That's all.

RoadMap:

* cut tweets if > 140
* dicsern and concatenate selected tags in more 'popular' one e.g #black += #hole > #blackhole 
* start new json if len([used_links]) > N
