# coding: utf-8
from __future__ import unicode_literals
import datetime

from app.utils import ScrapperHelper, Database


class Scrapper:

    def __init__(self):
        self.name = "L'Équipe"
        self.homepage_url = "http://www.lequipe.fr"
        self.watched_urls = []
        self.db = Database.NewspapersDatabase()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scrapper
        sc = ScrapperHelper.ScrapperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Main Column
        main_col = soup.select("#edito-gauche")[0]

        # Remove restricted members articles
        # standard articles
        [paid_article.extract() for paid_article in main_col.select(".premium")]
        # headlines
        for premium_icon in main_col.select(".iconPremium"):
            if premium_icon.parent.name == 'a':
                premium_icon.parent.extract()

        edito_standard_articles = main_col.select(".ZoneEdito a")
        edito_headline_articles = main_col.select(".EditoLeader a")

        articles = edito_headline_articles + edito_standard_articles

        # remove diaporamas
        [article.extract() for article in articles if '/Diaporama/' in article['href']]

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
        # Scrapper
        sc_article = ScrapperHelper.ScrapperHelper()
        soup_article = sc_article.getSoupFromPage(url)
        try:
            article_title = soup_article.select("h1 strong")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        try:
            article_creation_time = soup_article.select("time")[0]['datetime']
        except:
            article_creation_time = ''
        try:
            article_update_time = soup_article.select("time")[1]['datetime']
        except:
            article_update_time = ''
        try:
            if len(soup_article.find_all("meta", attrs={"property":"og:image"})) > 0:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image"})[0]['content']
            else:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image:url"})[0]['content']
        except:
            article_image_url = ''
        article_themes = [span.text.strip() for span in soup_article.select("h1 span")]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
