# coding: utf-8
from __future__ import unicode_literals
import datetime
import re
from app.utils import ScraperHelper, Database

class Scraper:

    def __init__(self):
        self.name = "Valeurs Actuelles"
        self.homepage_url = "http://www.valeursactuelles.com"
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
        articles = soup.select(".post h2 a")

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

    def encode_to_timecode_from_creation_text(self, raw_time):
        if raw_time == '':
            return ''
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre',
                      'Novembre', 'Décembre']
        for day in days:
            if day in raw_time:
                raw_time = raw_time.replace(day, "").strip()
        for idx, month in enumerate(months):
            if month in raw_time:
                raw_time = raw_time.replace(month, "%02d" % ((idx + 1),))
        if len(raw_time) == 18:
            #we have sth like : 18 05 2015 à 15:17
            #we want sth like : 2015-05-18T15:17:00+02:00
            raw_time = raw_time[6:10] + '-' + raw_time[3:5] + '-' + raw_time[0:2] + 'T'\
                       + raw_time[13:18] + ":00+02:00"
        else:
            raw_time = ''
        return raw_time

    def encode_to_timecode_from_update_text(self, raw_time):
        if raw_time == '':
            return ''
        if len(raw_time) == 18:
            #we have sth like : 18/05/2015 à 16:48
            #we want sth like : 2015-05-18T16:48:00+02:00
            raw_time = raw_time[6:10] + '-' + raw_time[3:5] + '-' + raw_time[0:2] + 'T'\
                       + raw_time[13:18] + ":00+02:00"
        else:
            raw_time = ''
        return raw_time

    def get_article_infos_and_log_into_DB(self,url):
        # Scraper
        sc_article = ScraperHelper.ScraperHelper()
        soup_article = sc_article.getSoupFromPage(url)
        try:
            article_title = soup_article.select("h2")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        text_date = soup_article.select(".date")[0].text.strip()
        try:
            # sth like : Lundi 18 Mai 2015 à 15:17
            creation_text = re.search('(.+?) \(mis à jour le', text_date).group(1)
            article_creation_time = self.encode_to_timecode_from_creation_text(creation_text)
        except:
            article_creation_time = ''
        try:
            # sth like : 18/05/2015 à 16:48
            update_text = re.search('mis à jour le (.+?)\)', text_date).group(1)
            article_update_time = self.encode_to_timecode_from_update_text(update_text)
        except:
            article_update_time = ''
        try:
            if len(soup_article.find_all("img", attrs={"typeof":"foaf:Image"})) > 0:
                article_image_url = soup_article.find_all("img", attrs={"typeof":"foaf:Image"})[0]['src']
            else:
                article_image_url = ''
        except:
            article_image_url = ''

        article_themes = [link.text.strip() for link in soup_article.select(".breadcrumbs a")
                                                if link.text.strip() != 'Accueil']

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
