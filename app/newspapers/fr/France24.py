# coding: utf-8
from __future__ import unicode_literals
import datetime
import re
from app.utils import ScraperHelper, Database

class Scraper:

    def __init__(self):
        self.name = 'France 24'
        self.homepage_url = "http://www.france24.com/fr"  # not a mistake
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
        articles  = soup.select(".col-1 .news-featured .title a")
        articles += soup.select(".col-1 .news-item a.modeless")
        articles += soup.select(".col-2 .featured-contents a")
        articles += soup.select(".col-2 .information-board .ib-item a")
        articles += soup.select(".wide-angle ul.slides p.default-read-more a.modeless")
        articles += soup.select(".our-programs ul.slides p.default-read-more a.modeless")

        articles_urls = list(set([article['href'] for article in articles if article.has_attr('href')]))

        for article_url in articles_urls:
            if article_url.startswith('/fr/'):
                self.keep_track_of(self.homepage_url.replace("/fr","") + article_url)
            elif self.homepage_url.replace("/fr","").replace("http://www.","") in article_url:
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

    def encode_to_timecode_from_text(self, raw_time):
        if raw_time == '':
            return ''
        if len(raw_time) == 10:
            #we have sth like : 19/05/2015
            #we want sth like : 2015-05-19T00:00:00+02:00
            raw_time = raw_time[6:10] + '-' + raw_time[3:5] + '-' + raw_time[0:2] + "T00:00:00+02:00"
        else:
            raw_time = ''
        return raw_time

    def get_article_infos_and_log_into_DB(self,url):
        # Scraper
        sc_article = ScraperHelper.ScraperHelper()
        soup_article = sc_article.getSoupFromPage(url)
        try:
            article_title = soup_article.select("h1.title")[0].text.strip()
        except:
            article_title = soup_article.title.string.strip()
        try:
            if len(soup_article.select("p.modification")) > 1:
                creation_text_str = soup_article.select("p.modification")[1].text.strip()  # creation after modification (!)
                # sth like : Première publication : 19/05/2015
                m = re.search('Première publication : ((?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.]'
                                          '(?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))'
                                          '(?![\\d])', creation_text_str)
                if m:
                    creation_text = m.group(1)
                    article_creation_time = self.encode_to_timecode_from_text(creation_text)
                else:
                    article_creation_time = ''
            else:
                article_creation_time = ''
        except:
            article_creation_time = ''
        try:
            if len(soup_article.select("p.modification")) > 0:
                update_text_str = soup_article.select("p.modification")[0].text.strip()  # creation after modification (!)
                # sth like : Dernière modification : 19/05/2015
                m = re.search('Dernière modification : ((?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.]'
                                        '(?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))'
                                        '(?![\\d])', update_text_str)
                if m:
                    update_text = m.group(1)
                    article_update_time = self.encode_to_timecode_from_text(update_text)
                else:
                    article_creation_time = ''
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

        # case www.france24.com :
        article_themes  = [link.text.strip() for link in soup_article.select(".main-board article header p.category a.modeless")]
        article_themes += [link.text.strip() for link in soup_article.select(".main-board article header ul li a.modeless")]
        # case observers.france24.com :
        article_themes += [link.text.strip() for link in soup_article.select(".story .article .terms li a")]
        # no theme for pages on webdocs.france24.com or grahics.france24.com

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
