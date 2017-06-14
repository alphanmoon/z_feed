## All prints() are for console testing, delete/comment while in production 

import feedparser, nltk, tweepy, json, random, time
from pyshorteners import Shortener

#Erasing [used links] in json for console testing, comment if no need
##used_links = []
##with open(used_file, 'w') as used:
##    json.dump(used_links, used)

check = ''

#Parsing a news title by iterating news feeds
while True:

    used_file = 'used_links_list_test.json'
    
    feed = ['https://foo.bar.foo.bar',
        'https://foo.bar.foo.bar',
        'https://foo.bar.foo.bar',
        ]
    
    # reloading feed list
    feed_run = feed
    
    while feed_run:
        # Randomly selecting then parsing feed
        select_feed = random.choice(feed_run)
        
        # Preventing series of tweets from the same source
        if select_feed == check:
            time.sleep(5)
            break
         
        d = feedparser.parse(select_feed)

        # Removing selected feed from actual run list
        feed_run.remove(select_feed)
        
        n_titles = len(d['entries'])  # COUNTING TITLES IN FEED
        
        # Iterating titles till a new one occurs, if yes - tweeting
        for i in range(n_titles):
            
            #Parsing a link from title                    
            url = d.entries[i].link  
            
            # Loading json with used links
            with open(used_file) as used:
                used_links = json.load(used)
            
            if url not in used_links:

                # Parsing title        
                post1 = d.entries[i].title
                    
                # Inserting hashtags in title nouns;  ******tag magic******
                toks = nltk.word_tokenize(post1)
                tags = nltk.pos_tag(toks)
                # 1stly make list from tuples
                tags_list = [list(elem) for elem in tags]           
                for t in tags_list:
                    if t[1] in ['NN', 'NNP']:                    
                        t[0] = '#' + t[0]
                    t[1] = ''
                   
                post2 = ' '.join([''.join(elem) for elem in tags_list])

                while True:
                    try:
                        api_key = 'YOUR_API_KEY'
                        shortener = Shortener('Google', api_key=api_key)
                        short_link = shortener.short(url)
                        if short_link:
                            break
                    except:               
                        time.sleep(30)

                #Building final post  
                post3 = post2 + ' ' + short_link
                if 139 > len(post3) > 10:

                    rsleep = random.randint(100,130)                    
                    #print('post is built, waiting %s sec' % rsleep)
                    time.sleep(rsleep)
                                      
                    #Tweeting
                    while True:                       
                        try:
                            CONSUMER_KEY = 'YOUR_KEY'
                            CONSUMER_SECRET = 'CONSUMER_SECRET'
                            ACCESS_KEY = ' ACCESS_KEY'
                            ACCESS_SECRET = 'ACCESS_SECRET'
                            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
                            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
                            api = tweepy.API(auth)
                            tweeted = api.update_status(post3)
                            if tweeted:
                                #print('tweeted! %s from %s' % (post3, select_feed))                        
                                break
                        except:
                            #print('tweepy error')
                            time.sleep(1000)
                            
                    # Saving used links in json
                    with open(used_file, 'w') as used:
                        used_links.append(url)
                        json.dump(used_links, used)
                        check = select_feed
                        #print('dump is OK')                        
                        break
                                
    #print('reloading feed list in n sec for the next random run')
    time.sleep(30)


