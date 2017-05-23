

import feedparser, nltk, tweepy, json, time
from pyshorteners import Shortener

used_file = 'used_links_list.json'

#Erasing [used links] in json in testing mode, comment when no need
used_links = []
with open(used_file, 'w') as used:
    json.dump(used_links, used)

# Insert rss feed url
feed = ['https://foo.bar.foo.bar', \
        'https://foo.bar.foo.bar', \
        'https://foo.bar.foo.bar',
        ]

#Parsing a news title by iterating news feeds
while True:
    #Parsing news feeds    
    for k in range(len(feed)):    
        d = feedparser.parse(feed[k])
        # TODO: COUNT TITLES IN FEED
        n_titles = len(d['entries'])
        for i in range(n_titles):    # SOME FEEDS ARE LESS THAN fixed no of TITLES CAUSING ERROR !!!!! hence COUNT TITLES IN FEEDS

            # Loading json with used links
            with open(used_file) as used:
                used_links = json.load(used)

            #Parsing a link from title                    
            url = d.entries[i].link

            # Adding used 'link' to a json list to exclude used news    
##            with open(used_file) as open_json:
##                links_old = json.load(open_json)
            if url not in used_links:
                used_links.append(url)
                with open(used_file, 'w') as used:
                    json.dump(used_links, used)
                    print('dump saved')

                # Parsing title        
                post1 = d.entries[i].title

                # Inserting hashtags afore title nouns;  ******magic******
                toks = nltk.word_tokenize(post1)
                tags = nltk.pos_tag(toks)
                # 1stly make list from tuples
                tags_list = [list(elem) for elem in tags]           
                for t in tags_list:
                    if t[1] in ['NN', 'NNP']:                    
                        t[0] = '#' + t[0]
                    t[1] = ''
                   
                post2 = ' '.join([''.join(elem) for elem in tags_list])
                #print(post2)    

                # Shortening url
                while True:
                    api_key = 'api_key'
                    shortener = Shortener('Google', api_key=api_key)
                    short_link = shortener.short(url)
                    if short_link:
                        print('link OK')
                        break

                #Building final post  
                post3 = post2 + ' ' + short_link
                if 139 > len(post3) > 40:                
                    print('post composed, waitin 10 sec then tweeting:', post3)

                    time.sleep(10)
    
                                          
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
                                print('tweeted!')
                                break
                        except:
                            print('tweepy error, sleepin 3 min')
                            time.sleep(180)

    else:
        print('no news')    
                                           
    print('Waiting 5 sec for the next cycle') 
    time.sleep(5)

