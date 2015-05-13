# coding: utf-8
from __future__ import unicode_literals
import datetime
from app.utils import ScrapperHelper, Database


class Scrapper:

    def __init__(self):
        self.name = 'Le Figaro'
        self.homepage_url = "http://www.lefigaro.fr"
        self.watched_urls = []
        self.db = Database.DatabaseJournaux()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scrapper
        sc = ScrapperHelper.ScrapperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Main Column
        main_col = soup.select(".fig-2cols .fig-main-col")[0]

        # Remove restricted members articles
        [paid_article.extract() for paid_article in main_col.select(".fig-profil-payant")]

        articles = main_col.select(".fig-profil-headline a")

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

    def clean_category(self, category):
        # Remove Restricted Articles
        for restricted_article in category.select(".marqueur_restreint"):
            # case restricted article in figcaption
            if restricted_article.parent.parent.parent.name == 'a':
                restricted_article.parent.parent.parent.extract()
            # standard case restricted article
            else:
                restricted_article.extract()
        # Remove Category Link (e.g. : /sport/ for Sport, /science/ for Science, ...)
        try:
            category.select(".entete_deroule")[0].extract()
        except:
            pass
        try:
            category.select(".tt6_capital")[0].extract()
        except:
            pass
        # Remove Subcategories
        try:
            [div.extract() for div in category.select(".sous_rub")]
        except:
            pass
        # Remove Bourse Link
        try:
            category.select(".bourse_widget_indices")[0].extract()
        except:
            pass
        # # Remove Live icon, Play icon, etc.
        # try:
        #     [div.extract() for div in category.select(".img_ico")]
        # except:
        #     pass
        # Remove ads
        [ad.extract() for ad in category.select(".annonce")]
        [ad.extract() for ad in category.select(".intitule")]
        # Remove type
        [article_type.extract() for article_type in category.select(".type_element")]
        # Remove idees ensemble
        for link in category.select("a"):
            if "/ensemble/" in link['href']:
                link.extract()
        # Remove 'twitter', 'post_blog' articles
        [image.parent.parent.extract() for image in category.find_all("img", attrs={"data-item-type":"twitter"})]
        [image.parent.parent.extract() for image in category.find_all("img", attrs={"data-item-type":"post_blog"})]
        # Remove nb comments
        [comment_count.extract() for comment_count in category.select(".nb_reactions")]
        # Remove blogs articles
        try:
            category.select(".bloc_deroule_blogs")[0].extract()
        except:
            pass
        return category

    def keep_track_of(self, url):
        self.watched_urls.append(url)

    def get_article_infos_and_log_into_DB(self,url):
        # Scrapper
        sc_article = ScrapperHelper.ScrapperHelper()
        soup_article = sc_article.getSoupFromPage(url)

        [tag.extract() for tag in soup_article.select(".fig-tag-avant-premiere")]

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
        article_themes = [li.find("a", attrs={"class":"fig-breadcrumb-rubrique"}).text for li in soup_article.find_all("li", attrs={"class":"fig-breadcrumb"})]

        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
