# coding: utf-8
from __future__ import unicode_literals
import datetime
import re
from app.utils import ScraperHelper, Database


class Scraper:

    def __init__(self):
        self.name = "La Croix"
        self.homepage_url = "http://www.la-croix.com"
        self.watched_urls = []
        self.db = Database.NewspapersDatabase()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scraper
        sc = ScraperHelper.ScraperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Remove comments, the 'all' editos link, the diaporama
        [comments.extract() for comments in soup.select(".comments")]
        [all_editos.extract() for all_editos in soup.select(".link_all")]
        [diaporama.extract() for diaporama in soup.select(".diaporama2")]
        # Remove services
        [service.extract() for service in soup.select("#zone_service")]

        # Articles
        articles = soup.select("#layout_lacroix .mea_actu a")

        articles_urls = list(set([article['href'] for article in articles if article.has_attr('href')]))
        articles_urls = [article_url for article_url in articles_urls if ('.blogs.' not in article_url
                                                                          and article_url.count('/') > 1)]

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
        if len(raw_time) == 16:
            raw_time = raw_time + ":00+02:00"
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
        article_creation_time = self.encode_to_timecode(article_creation_time)
        try:
            article_update_time = soup_article.find(attrs={"itemprop":"dateModified"})['content']
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

        article_themes = [link.text.strip() for link in soup_article.select(".fildariane a")]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
