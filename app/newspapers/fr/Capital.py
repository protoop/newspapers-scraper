# coding: utf-8
from __future__ import unicode_literals
import datetime
import re
from app.utils import ScraperHelper, Database


class Scraper:

    def __init__(self):
        self.name = 'Capital'
        self.homepage_url = "http://www.capital.fr"
        self.watched_urls = []
        self.db = Database.NewspapersDatabase()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scraper
        sc = ScraperHelper.ScraperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Articles
        # (some links are in double, but are de-duplicated just after (with the lis(set(...)))
        articles = soup.select("#left_main .article a") # main articles
        articles += soup.select(".elementactu a")       # small newsfeed articles

        articles_urls = list(set([article['href'] for article in articles if article.has_attr('href')]))

        for article_url in articles_urls:
            if article_url.startswith('/'):
                self.keep_track_of(self.homepage_url + article_url)
            elif self.homepage_url.replace("http://www.","") in article_url:
                self.keep_track_of(article_url)
            else:
                pass

        # Get Title, Image, Creation & Update Time
        for pos, url in enumerate(self.watched_urls):
            print self.name, ":", (pos+1), "/", len(self.watched_urls), ":", url
            try:
                self.get_article_infos_and_log_into_DB(url)
            except:
                print '[ERR] An error occurred when fetching an article from ', self.name, '( timestamp :', datetime.datetime.now(), ').'
                print '   ---> ERR URL :', url

    def keep_track_of(self, url):
        self.watched_urls.append(url)

    def encode_to_timecode(self, raw_time):
        if raw_time == '':
            return ''
        #we have sth like :  13/05/158:45 or 13/05/1519:45
        #we want sth like :  2015-05-13 08:45:00+02:00
        if len(raw_time) == 12:
            raw_time = '20' + raw_time[6:8] + '-' + raw_time[3:5] + '-' + raw_time[0:2]\
                        + ' ' + '0' + raw_time[8:12] + ':00+02:00'
        elif len(raw_time) == 13:
            raw_time = '20' + raw_time[6:8] + '-' + raw_time[3:5] + '-' + raw_time[0:2]\
                        + ' ' + raw_time[8:13] + ':00+02:00'
        else:
            raw_time = ''
        return raw_time

    def get_article_infos_and_log_into_DB(self,url):
        # Scraper
        sc_article = ScraperHelper.ScraperHelper()
        soup_article = sc_article.getSoupFromPage(url)
        try:
            article_title = soup_article.select("h1")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        try:
            article_creation_time = soup_article.find(attrs={"itemprop":"datePublished"})['content']
        except:
            article_creation_time = ''
        try:
            # In plain text...
            article_update_time_plain_text = soup_article.select("p.update")[0].text.strip()
            # Regex generated by http://txt2re.com/ ;)
            re1 = '.*?'	# Non-greedy match on filler
            re2 = '((?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:\\d{1}\\d{1})))(?![\\d])'	# DDMMYY 1
            re3 = '.*?'	# Non-greedy match on filler
            re4 = '((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'	# HourMinuteSec 1
            rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
            m = rg.search(article_update_time_plain_text)
            if m:
                ddmmyy = m.group(1) # format : DD/MM/YY
                time = m.group(2)   # e.g. 9:52 or 17:59
                article_update_time = self.encode_to_timecode(ddmmyy + time)
            else:
                article_update_time = ''
        except:
            article_update_time = ''
        try:
            if len(soup_article.find_all("meta", attrs={"property":"og:image"})) > 0:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image"})[0]['content']
            else:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image:url"})[0]['content']
        except:
            article_image_url = ''

        article_themes = [link.text.strip() for link in soup_article.select(".breadcrumb a")]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
