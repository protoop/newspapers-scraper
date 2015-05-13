# coding: utf-8
from __future__ import unicode_literals
import datetime
from app.utils import ScraperHelper, Database


class Scraper:

    def __init__(self):
        self.name = 'Le Monde'
        self.homepage_url = "http://www.lemonde.fr"
        self.watched_urls = []
        self.db = Database.NewspapersDatabase()
        if not self.db.is_newspaper_in_database(self.name):
            self.db.insert_newspaper_in_database(self.name, self.homepage_url)
        self.newspaper_id = self.db.get_newspaper_id_from_database(self.name)

    def start_scrapping_articles_found_on_homepage(self):

        # Scraper
        sc = ScraperHelper.ScraperHelper()
        soup = sc.getSoupFromPage(self.homepage_url)

        # Categories : Edito
        edito = soup.select(".global.une_edito")[0]

        # Categories : Standard categories
        videos = soup.select(".global.videos")[0]
        grands_formats = soup.select(".global.grands_formats")[0]
        sport = soup.select(".global.sport")[0]
        magazine = soup.select(".global.m-mag")[0]
        decodeurs = soup.select(".global.les-decodeurs")[0]
        pixels = soup.select(".global.pixels")[0]
        sciences = soup.select(".global.sciences")[0]
        international = soup.select(".global.international")[0]
        politique = soup.select(".global.politique")[0]
        economie = soup.select(".global.economie")[0]
        societe = soup.select(".global.societe")[0]
        planete = soup.select(".global.planete")[0]
        campus = soup.select(".global.campus")[0]
        culture = soup.select(".global.culture")[0]
        idees = soup.select(".global.idees")[0]

        # Categories : Edito
        self.start_scrapping_the_edito_category(edito)

        # Categories : Standard categories
        self.start_scrapping_this_generic_category(videos)
        self.start_scrapping_this_generic_category(grands_formats)
        self.start_scrapping_this_generic_category(sport)
        self.start_scrapping_this_generic_category(magazine)
        self.start_scrapping_this_generic_category(decodeurs)
        self.start_scrapping_this_generic_category(pixels)
        self.start_scrapping_this_generic_category(sciences)
        self.start_scrapping_this_generic_category(international)
        self.start_scrapping_this_generic_category(politique)
        self.start_scrapping_this_generic_category(economie)
        self.start_scrapping_this_generic_category(societe)
        self.start_scrapping_this_generic_category(planete)
        self.start_scrapping_this_generic_category(campus)
        self.start_scrapping_this_generic_category(culture)
        self.start_scrapping_this_generic_category(idees)

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
        # Remove Real-estate Links
        try:
            [a.extract() for a in category.select("a") if a.has_attr('href') and ('immobilier-prestige' in a['href']
                                                                                  or 'immobilier.lemonde.fr' in a['href'])]
        except:
            pass
        # Remove Stock Exchange Links
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
        # Remove 'ensemble' ideas
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

    def start_scrapping_the_edito_category(self, category):
        # Remove garbage
        category = self.clean_category(category)
        # Headline
        une_newspaper = category.select(".une_evenement")
        if une_newspaper == []:
            une_newspaper = category.select(".une_normale")
        # Titres
        titres_liste = category.select(".titres_liste")

        # Get links
        titres_liste_links = titres_liste[0].find_all("a")
        une_newspaper_links = une_newspaper[0].find_all("a")

        edito_articles = titres_liste_links + une_newspaper_links

        edito_articles_urls = list(set([article['href'] for article in edito_articles if article.has_attr('href')]))

        for edito_article_url in edito_articles_urls:
            if edito_article_url.startswith('/'):
                self.keep_track_of(self.homepage_url + edito_article_url)
            elif self.homepage_url.replace("http://www.","") in edito_article_url:
                self.keep_track_of(edito_article_url)
            else:
                pass

    def start_scrapping_this_generic_category(self, category):
        category = self.clean_category(category)
        category_links = category.find_all("a")

        generic_articles_urls = list(set([article['href'] for article in category_links if article.has_attr('href')]))

        for generic_article_url in generic_articles_urls:
            if generic_article_url.startswith('/'):
                self.keep_track_of(self.homepage_url + generic_article_url)
            elif self.homepage_url.replace("http://www.","") in generic_article_url:
                self.keep_track_of(generic_article_url)
            else:
                pass

    def keep_track_of(self, url):
        self.watched_urls.append(url)

    def get_article_infos_and_log_into_DB(self,url):
        # Scraper
        sc_article = ScraperHelper.ScraperHelper()
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
        article_themes = [li.find("a").text for li in soup_article.find_all("li", attrs={"class":"ariane"})]
        self.db.log_article_to_database(self.newspaper_id, url, article_title, article_themes, article_creation_time, article_update_time, article_image_url)
