# coding: utf-8
from __future__ import unicode_literals
import datetime

from app.utils import ScrapperHelper, Database


class Scrapper:

    def __init__(self):
        self.name = 'Metro News'
        self.homepage_url = "http://www.metronews.fr"
        self.watched_urls = []
        self.db = Database.DatabaseJournaux()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scrapper
        sc = ScrapperHelper.ScrapperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Articles
        articles = soup.select(".column-item a")
        # Remove ads
        [r.extract() for r in articles if not (r['href'].startswith('/')
                                               or r['href'].startswith(self.homepage_url.replace("www.",""))
                                               or r['href'].startswith(self.homepage_url))]

        # Remove Metrozap & ClubMetro
        articles = [r for r in articles if ("metrozap" not in r['href'] and "clubmetro" not in r['href'])]
        # Remove Games
        articles = [r for r in articles if ("/jeux/" not in r['href'])]
        # Remove blogs
        articles = [r for r in articles if ("/blog/" not in r['href'])]

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
            article_title = soup_article.select("h1")[0].text.strip()
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

        article_themes = [link.text for link in soup_article.select("#b-nav a") if ('accueil' != link.text and '>' != link.text)]
        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
