import feedparser, nltk, random, time, sqlite3, tweepy, shutil, os
from datetime import datetime
from pyshorteners import Shortener
from pyshorteners.exceptions import UnknownShortenerException, ShorteningErrorException, ExpandingErrorException
from requests.exceptions import Timeout, ReadTimeout
from z_secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET, api_key, PATH2DB, PATH2DB_BCKUP


check = []

reload_count = 0

zb = sqlite3.connect(PATH2DB)
c = zb.cursor()

# Backup DB after n reloads of feeds list
def backup_db():
    shutil.copyfile(PATH2DB, PATH2DB_BCKUP)
    print('db backed')

def parsefeed(select_feed):
        try:
            d1 = feedparser.parse(select_feed)
            return d1
        except:
            return False


def tagging():
    # Inserting hashtags in title nouns using NLTK;  ******tag magic******
    toks = nltk.word_tokenize(post1)
    tags = nltk.pos_tag(toks)
    # make list from tuples
    tags_list = [list(elem) for elem in tags]
    for t in tags_list:
        if t[1] in ['NN', 'NNP']:
            t[0] = '#' + t[0]
        t[1] = ''
    return tags_list


# Def func for adding data to DB
def data_entry(zb):
    tstamp = datetime.now()
    c.execute("insert into zbase values(?, ?, ?, ?)", (tstamp, select_feed, post1, url))
    zb.commit()
    print('data OK')


def shortening(url):
        try:
            shortener = Shortener('Google', api_key=api_key)
            short_link = shortener.short(url)
            return short_link
        except UnknownShortenerException as e:
            e1 = str(e)
            dt = str(datetime.now())
            c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, '', '', e1, '', url))
            zb.commit()
            return False
        except ShorteningErrorException as e:
            e1 = str(e)
            dt = str(datetime.now())
            c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, '', '', e1, '', url))
            zb.commit()
            return False
        except ExpandingErrorException as e:
            e1 = str(e)
            dt = str(datetime.now())
            c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, '', '', e1, '', url))
            zb.commit()
            return False
        except ReadTimeout as e:
            e1 = str(e)
            print(e1)
            dt = str(datetime.now())
            c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, '', '', e1, '', url))
            zb.commit()
            return False


def tweeting(post3, select_feed, T_SLEEP):
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            api = tweepy.API(auth)
            api.update_status(post3)
            return True

        except tweepy.TweepError as e:
            e1 = str(e)
            dt = str(datetime.now())
            c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, '', e1, '', post3, select_feed))
            zb.commit()
            return False


def checkfeeds(check, select_feed):
    # Preventing frequent tweets from hyperactive feeds/sources in n runs using var S_FACTOR from z_tuning module
    if len(check) > S_FACTOR:
        check = []
        c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (datetime.now(), 'CHECK RELOAD', '', '', '', ''))
        zb.commit()
        return check
    else:
        c.execute("select SOURCE from zfeeds where FEED = '%s'" % select_feed)
        source = c.fetchall()
        check.append(source)
        return check


while True:
    try:
        from z_tuning import S_FACTOR, U_SLEEP, T_SLEEP, TIME_MIN, TIME_MAX, RELOADS_N

        # reloading feeds list from DB
        c.execute('select FEED from zfeeds')
        feed_run = list(sum(c.fetchall(), ()))

        # Write to db-log
        dt = datetime.now()
        c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, 'FEEDS RELOAD', '',  '', '', ''))
        zb.commit()

        # Backup DB after n feedsreload
        reload_count += 1
        print(reload_count)

        if reload_count > RELOADS_N:
            backup_db()
            reload_count = 0

        while feed_run:
            # Randomly selecting then parsing a feed
            select_feed = random.choice(feed_run)

            d = parsefeed(select_feed)

            if d is False:
                break

            # # Removing selected feed from actual run list
            feed_run.remove(select_feed)

            # Counting titles in feed
            n_titles = len(d['entries'])

            # Iterating titles in a feed till a new one occurs, if yes - tweeting
            for i in range(n_titles):

                # Parsing a link from title
                url = d.entries[i].link
                c.execute('select LINK from zbase')
                used = c.fetchall()
                used_links = [item for sublist in used for item in sublist]

                if url not in used_links:
                    # Preventing frequent tweets from the most active feeds
                    c.execute("select SOURCE from zfeeds where FEED = '%s'" % select_feed)
                    source = c.fetchall()
                    if source in check:
                        dt = datetime.now()
                        c.execute("insert into zfeed_log values(?, ?, ?, ?, ?, ?)", (dt, 'FEED CHANGE', '', '', '', ''))
                        zb.commit()
                        break

                    # Parsing title from feed
                    post1 = d.entries[i].title
                    print(select_feed, post1)

                    # Make post with tagged NOUNS using tagging()
                    post2 = ' '.join([''.join(elem) for elem in tagging()])

                    short_link = shortening(url)

                    if short_link is False:
                        time.sleep(U_SLEEP)
                        break

                    # Building final post
                    post3 = post2 + ' ' + short_link

                    # Tweeting
                    if 139 > len(post3) > 10:

                        tweeted = tweeting(post3, select_feed, T_SLEEP)

                        if tweeted is False:
                            time.sleep(T_SLEEP)
                            break
                            # time.sleep(T_SLEEP)
                            # for n in range(5):
                            #     tweeted2 = tweeting(post3)
                            #     time.sleep(T_SLEEP)
                            #     if tweeted2:
                            #         break
                            # if tweeted2 is False:
                            #     break

                        check = checkfeeds(check, select_feed)
                        print(len(check))

                        data_entry(zb)

                        rsleep = random.randint(TIME_MIN, TIME_MAX)
                        time.sleep(rsleep)
                        break

                    elif len(post3) > 139:
                        post3 = post2[:115] + ".." + short_link

                        tweeted = tweeting(post3, select_feed, T_SLEEP)

                        if tweeted is False:
                            break
                            # time.sleep(T_SLEEP)
                            # for n in range(5):
                            #     tweeted2 = tweeting(post3)
                            #     time.sleep(T_SLEEP)
                            #     if tweeted2:
                            #         break
                            # if tweeted2 is False:
                            #     break

                        check = checkfeeds(check, select_feed)
                        print(len(check))

                        data_entry(zb)

                        rsleep = random.randint(TIME_MIN, TIME_MAX)
                        time.sleep(rsleep)
                        break

    except Exception as e:
        f = open('zdb_log', 'a')
        f.write('{0} {1}\n'.format(str(datetime.now()), str(e)))
        f.close()
        print('err put in log')
        time.sleep(3)
