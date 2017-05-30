# z_feed
Just another tweeting python bot with hashtags inserting smart machine


* reads news feeds, 
* makes title parsing,
* sets keywords in titles by spoting NOUNs
* inserts hashtags afore keywords
* builds posts and tweets 'em
* waits for next news coming 

That's all.

RoadMap:

* cut tweets if > 140
* discern and concatenate selected tags in more 'popular' one e.g #black += #hole > #blackhole 
* start new json if len([used_links]) > N
* tweet by schedule using tweets depot 
* hot tags monitoring
* DONE: randomize rolling tweets by source 
* DONE: randomize tweeting time step
