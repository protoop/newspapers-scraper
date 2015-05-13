# coding: utf-8
from __future__ import unicode_literals
import datetime

from app.utils import ScrapperHelper, Database


class Scrapper:

    def __init__(self):
        self.name = "L'Express"
        self.homepage_url = "http://www.lexpress.fr"
        self.watched_urls = []
        self.db = Database.NewspapersDatabase()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scrapper
        sc = ScrapperHelper.ScrapperHelper()
        soup = sc.getSoupFromPage(self.homepage_url, 'ISO-8859-1')

        # Remove blogs
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and 'blogs.' in link['href'])]
        # Remove styles & 24h images section
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and '/styles/' in link['href'])]
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and '/24henimage/' in link['href'])]

        # Articles
        articles_une_main = soup.select("#content .une .item_fleuve_title a")
        articles_une_plus = soup.select("#content .une .sommaire a")
        articles_standard_main = soup.select("#content .fleuve .item_fleuve .item_fleuve_title a")
        articles_standard_plus = soup.select("#content .fleuve .item_fleuve .sommaire a")
        articles_videos = soup.select("#content .fleuve .fleuve_2_items.headline a.visual")

        articles = articles_une_main + articles_une_plus + articles_standard_main + articles_standard_plus + articles_videos

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
        if len(raw_time) != 19:  #see below for the length == 19
            return ''
        #we now have sth like :  09/05/2015 17:34:08    <-- length==19
        #we want sth like :  2015-05-09 17:34:08+02:00
        try:
            raw_time = raw_time[6:10] + '-' + raw_time[3:5] + '-' + raw_time[0:2]\
                                      + ' ' + raw_time[11:13] + ':' + raw_time[14:16]+ ':' + raw_time[17:19] + '+02:00'
        except:
            raw_time = ''
        return raw_time

    def get_article_infos_and_log_into_DB(self,url):
        # Scrapper
        sc_article = ScrapperHelper.ScrapperHelper()
        soup_article = sc_article.getSoupFromPage(url, 'ISO-8859-1')
        try:
            article_title = soup_article.select("h1")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        try:
            article_creation_time = soup_article.select("time")[0]['datetime']
        except:
            article_creation_time = ''
        article_creation_time = self.encode_to_timecode(article_creation_time)
        try:
            article_update_time = soup_article.select("time")[1]['datetime']
        except:
            article_update_time = ''
        article_update_time = self.encode_to_timecode(article_update_time)
        try:
            if len(soup_article.find_all("meta", attrs={"property":"og:image"})) > 0:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image"})[0]['content']
            else:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image:url"})[0]['content']
        except:
            article_image_url = ''

        article_themes = [link.text for link in soup_article.select(".breadcrumb a")]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
