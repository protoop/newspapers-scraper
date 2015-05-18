# coding: utf-8
from __future__ import unicode_literals
import datetime
from app.utils import ScraperHelper, Database

class Scraper:

    def __init__(self):
        self.name = 'France Inter'
        self.homepage_url = "http://www.franceinter.fr"
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
        articles_une = soup.select(".item-une .title a")
        articles_others = soup.select(".item-fleuve h3 a")

        articles = articles_une + articles_others

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

    def get_article_infos_and_log_into_DB(self,url):
        # Scraper
        sc_article = ScraperHelper.ScraperHelper()
        soup_article = sc_article.getSoupFromPage(url)
        try:
            if len(soup_article.select(".entete h1")) > 0:
                article_title = soup_article.select(".entete h1")[0].text.strip()
            else:
                article_title = soup_article.select(".entete h2")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        # No time !!! (in almost each case, or too "dirty")
        article_creation_time = ''
        # No time !!! (in almost each case, or too "dirty")
        article_update_time = ''
        try:
            if len(soup_article.find_all("meta", attrs={"property":"og:image"})) > 0:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image"})[0]['content']
            else:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image:url"})[0]['content']
        except:
            article_image_url = ''

        # (No error in the breadcrumb's class name)
        article_themes = [link.text.strip() for link in soup_article.select(".date .noir")]
        if len(article_themes) == 0:
            article_themes = [img['title'] for img in soup_article.select(".une .title img") if img.has_attr('title')]

        # The data gathered are *very* dirty...
        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
