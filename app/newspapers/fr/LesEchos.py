# coding: utf-8
from __future__ import unicode_literals
import datetime

from app.utils import ScrapperHelper, Database


class Scrapper:

    def __init__(self):
        self.name = 'Les Echos'
        self.homepage_url = "http://www.lesechos.fr"
        self.watched_urls = []
        self.db = Database.DatabaseJournaux()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scrapper
        sc = ScrapperHelper.ScrapperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Remove partners ads
        [ad.extract() for ad in soup.select(".nospartenaires")]
        # Remove supplements
        [link.extract() for link in soup.select("a") if link.has_attr('href') and '/supplement/' in link['href']]

        # Articles
        articles_type1 = soup.select(".type1 a.lien-titrepos1")
        articles_type2 = soup.select(".type2 a")
        articles_type3 = soup.select(".type3 a")
        articles_more = soup.select(".titre-puce a")
        articles_videos = soup.select(".blocarticle a")
        articles = articles_type1 + articles_type2 + articles_type3 + articles_more + articles_videos

        articles_urls = list(set([article['href'] for article in articles])) #list(set(..)) for uniq. urls

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

    def encode_to_timecode(self, raw_time):
        if raw_time == '':
            return ''
        if len(raw_time) == 25:
            return raw_time
        try:
            raw_time = raw_time.replace(" CEST", "+02:00").strip() #including the space before CEST
            raw_time = raw_time.replace(" CET", "+01:00").strip() #including the space before CET
            raw_time.replace(" ", "-")
            days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            for day in days:
                if day in raw_time:
                    raw_time = raw_time.replace(day, "").strip()
            days = ['lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.', 'dim.']
            for day in days:
                if day in raw_time:
                    raw_time = raw_time.replace(day, "").strip()
            days = ['lun.', 'mar.', 'mercr.', 'jeu.', 'vendr.', 'sam.', 'dim.']
            for day in days:
                if day in raw_time:
                    raw_time = raw_time.replace(day, "").strip()
            months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            for idx, month in enumerate(months):
                if month in raw_time:
                    raw_time = raw_time.replace(month, "%02d" % ((idx + 1),))
            months = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juill.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
            for idx, month in enumerate(months):
                if month in raw_time:
                    raw_time = raw_time.replace(month, "%02d" % ((idx + 1),))
            if raw_time[4:5] == '-' and raw_time[7:8] and len(raw_time) == 16:
                    raw_time = raw_time + ':00+02:00'
            if len(raw_time) < 25:  #see below for the length == 25
                return ''
            if raw_time[4:5] != '-':  #bad format : year should come first, then the month, ...
                raw_time = raw_time[6:10] + '-' + raw_time[3:5] + '-' + raw_time[0:2] + '-' + raw_time[11:]
        except:
            raw_time = ''
        return raw_time

    def keep_track_of(self, url):
        self.watched_urls.append(url)

    def get_article_infos_and_log_into_DB(self,url):
        # Scrapper
        sc_article = ScrapperHelper.ScrapperHelper()
        soup_article = sc_article.getSoupFromPage(url)

        # Remove categories titles
        [header_cat.extract() for header_cat in soup_article.select(".header-rubrique")]

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

        article_themes = [link.text.strip() for link in soup_article.select("#ariane a") if 'Accueil' != link.text]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
