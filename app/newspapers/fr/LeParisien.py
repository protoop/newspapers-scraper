# coding: utf-8
from __future__ import unicode_literals
import re
import datetime
from app.utils import ScrapperHelper, Database


class Scrapper:

    def __init__(self):
        self.name = 'Le Parisien'
        self.homepage_url = "http://www.leparisien.fr"
        self.watched_urls = []
        self.db = Database.DatabaseJournaux()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scrapper
        sc = ScrapperHelper.ScrapperHelper()
        soup = sc.getSoupFromPage(self.homepage_url, 'ISO-8859-1')

        # Remove Headlines Categories from the bottom of the page
        [category.extract() for category in soup.select(".parisien-section.dernieresactus h1")]
        # Remove promos
        soup.select(".parisien-section.dernieresactus article")[-1].extract()
        # Remove blogs
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and '.blog.' in link['href'])]
        # Remove premium content
        [link.extract() for link in soup.select("a") if (link.has_attr('href') and '/espace-premium/' in link['href'])]

        # Articles
        articles = soup.select(".parisien-section article a")

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
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        for day in days:
            if day in raw_time:
                raw_time = raw_time.replace(day, "").strip()
        for idx, month in enumerate(months):
            if month in raw_time:
                raw_time = raw_time.replace(month, "%02d" % ((idx + 1),))
        if len(raw_time) != 17:  #see below for the length == 17
            return ''
        #we now have sth like :  09 05 2015, 12h13    <-- length==17
        #we want sth like :  2015-05-09 12:13:00+02:00
        raw_time = raw_time[6:10] + '-' + raw_time[3:5] + '-' + raw_time[0:2]\
                                  + ' ' + raw_time[12:14] + ':' + raw_time[15:17] + ':00+2:00'
        return raw_time

    def get_article_infos_and_log_into_DB(self,url):
        # Scrapper
        sc_article = ScrapperHelper.ScrapperHelper()
        soup_article = sc_article.getSoupFromPage(url)
        try:
            article_title = soup_article.select("#contTitre h1")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        try:
            if '/video/' in url:
                raw_article_creation_time = soup_article.select("#infosArticle p")[0].text
            else:
                auth_line = soup_article.select("span.auteur")[0].text
                if auth_line.count('|') == 1:
                    if '20' in auth_line: #(2015 for instance, i.e. it's a date)
                        raw_article_creation_time = re.findall(r'(.*)\|', auth_line)[0].strip()
                    # else ... maybe it is just the author ? ==> exception
                elif auth_line.count('|') == 2:
                    raw_article_creation_time = re.findall(r'\|(.*)\|', auth_line)[0].strip()
        except:
            raw_article_creation_time = ''
        article_creation_time = self.encode_to_timecode(raw_article_creation_time)
        try:
            if '/video/' in url:
                raw_article_update_time = ''
            else:
                auth_line = soup_article.select("span.auteur")[0].text
                raw_article_update_time = re.findall(r'MAJ :(.*)', auth_line)[0].strip()
        except:
            raw_article_update_time = ''
        article_update_time = self.encode_to_timecode(raw_article_update_time)
        try:
            if len(soup_article.find_all("meta", attrs={"property":"og:image"})) > 0:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image"})[0]['content']
            else:
                article_image_url = soup_article.find_all("meta", attrs={"property":"og:image:url"})[0]['content']
        except:
            article_image_url = ''

        article_themes = [link.text for link in soup_article.select("#filAriane span")]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
