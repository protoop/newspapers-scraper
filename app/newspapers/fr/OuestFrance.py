# coding: utf-8
from __future__ import unicode_literals
import datetime
from app.utils import ScraperHelper, Database


class Scraper:

    def __init__(self):
        self.name = 'Ouest France'
        self.homepage_url = "http://www.ouest-france.fr"
        self.watched_urls = []
        self.db = Database.NewspapersDatabase()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scraper
        sc = ScraperHelper.ScraperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Remove premium articles
        [r.extract() for r in soup.select(".mc-promo-journal")]
        # Remove comments
        [r.extract() for r in soup.select(".meta-comments a")]
        # Remove blogs
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and '.blogs.' in link['href'])]
        # Remove javascript
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and 'javascript:' in link['href'])]
        # Remove La Une
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and '/la-une-' in link['href'])]

        # Articles
        articles_1 = soup.select(".blc-liens-seo a")
        articles_2 = soup.select("article a")
        articles = articles_1 + articles_2

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
        raw_time = raw_time.replace("Z", "+02:00")
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
            if len(soup_article.find_all("time", attrs={"itemprop":"datepublished"})) > 0:
                article_creation_time = soup_article.find_all("time", attrs={"itemprop":"datepublished"})[0]['datetime']
            else:
                article_creation_time = soup_article.select("time")[0]['datetime']
        except:
            article_creation_time = ''
        article_creation_time = self.encode_to_timecode(article_creation_time)
        try:
            if len(soup_article.find_all("time", attrs={"itemprop":"dateupdated"})) > 0:
                article_update_time = soup_article.find_all("time", attrs={"itemprop":"dateupdated"})[0]['datetime']
            else:
                article_update_time = ''
            if article_update_time == article_creation_time:
                article_update_time = ''
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

        article_themes = [link.text.strip() for link in soup_article.select("#breadcrumb a") if 'Accueil' != link.text.strip()]
        filter(None, article_themes)

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
