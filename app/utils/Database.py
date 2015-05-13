# coding: utf-8
from __future__ import unicode_literals
import sqlite3  #https://docs.python.org/2/library/sqlite3.html
import os
from time import strftime  #gmtime
from app import Config
from . import ScraperHelper


class NewspapersDatabase:
    def __init__(self):
        config = Config.Config()
        os.chdir(config.get_database_path())
        self.conn = sqlite3.connect(config.get_database_file_name())
        self.c = self.conn.cursor()

        # Only for DEBUG or DEV
        # self.c.execute('''DROP TABLE IF EXISTS newspaper''')         #Debug
        # self.c.execute('''DROP TABLE IF EXISTS article''')           #Debug
        # self.c.execute('''DROP TABLE IF EXISTS theme''')             #Debug
        # self.c.execute('''DROP TABLE IF EXISTS timeline_point''')    #Debug
        # self.c.execute('''DROP TABLE IF EXISTS theme_article_jointure''')    #Debug
        # END of DEBUG or DEV

        self.c.execute('''
        CREATE TABLE IF NOT EXISTS newspaper
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT
        )
        ''')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS article
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url text,
            image_url TEXT,
            id_newspaper INTEGER
        )
        ''')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS theme
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
        ''')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS timeline_point
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            point_type TEXT,
            id_article INTEGER
        )
        ''')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS theme_article_jointure
        (
            id_theme INTEGER,
            id_article INTEGER
        )
        ''')

    def insert_newspaper_in_database(self, name, url):
        sql = """
        INSERT INTO newspaper
        (
            name,
            url
        )
        VALUES (?,?)
        """
        sql_args = (name, url)
        self.c.execute(sql, sql_args)
        self.conn.commit()

    def insert_article_in_database(self, title, url, image_url, id_newspaper):
        sql = """
        INSERT INTO article
        (
            title,
            url,
            image_url,
            id_newspaper
        )
        VALUES (?,?,?,?)
        """
        sql_args = (title, url, image_url, id_newspaper)
        self.c.execute(sql, sql_args)
        self.conn.commit()

    def insert_theme_in_database(self, name):
        sql = """
        INSERT INTO theme
        (
            name
        )
        VALUES (?)
        """
        sql_args = (name)
        self.c.execute(sql, sql_args)
        self.conn.commit()

    def insert_timeline_point_in_database(self, time, point_type, id_article):
        sql = """
        INSERT INTO timeline_point
        (
            time,
            point_type,
            id_article
        )
        VALUES (?,?,?)
        """
        sql_args = (time, point_type, id_article)
        self.c.execute(sql, sql_args)
        self.conn.commit()

    def insert_theme_article_jointure_in_database(self, id_theme, id_article):
        sql = """
        INSERT INTO theme_article_jointure
        (
            id_theme,
            id_article
        )
        VALUES (?,?)
        """
        sql_args = (id_theme, id_article)
        self.c.execute(sql, sql_args)
        self.conn.commit()

    def is_newspaper_in_database(self, name):
        response = False
        for row in self.c.execute('SELECT * FROM newspaper WHERE name=?', (name,)):
            response = True
        return response

    def is_article_in_database(self, url):
        if self.get_article_from_database(url) is None:
            return False
        else:
            return True

    def is_theme_in_database(self, name):
        response = False
        for row in self.c.execute('SELECT * FROM theme WHERE name=?', (name,)):
            response = True
        return response

    def get_newspaper_from_database(self, name):
        self.c.execute('SELECT * FROM newspaper WHERE name=?', (name,))
        newspaper = self.c.fetchone()
        return newspaper

    def get_newspaper_id_from_database(self, name):
        newspaper = self.get_newspaper_from_database(name)
        if newspaper is None:
            return None
        else:
            return newspaper[0]

    def get_article_from_database(self, url):
        self.c.execute('SELECT * FROM article WHERE url=?', (url,))
        article = self.c.fetchone()
        return article

    def get_article_id_from_database(self, url):
        article = self.get_article_from_database(url)
        if article is None:
            return None
        else:
            return article[0]

    def get_theme_from_database(self, name):
        self.c.execute('SELECT * FROM theme WHERE name=?', (name,))
        theme = self.c.fetchone()
        return theme

    def get_theme_id_from_database(self, name):
        theme = self.get_theme_from_database(name)
        if theme is None:
            return None
        else:
            return theme[0]

    def add_a_timeline_point_update_if_needed(self, article_url, last_update_time_found):
        id_article = self.get_article_id_from_database(article_url)
        self.c.execute('SELECT * FROM timeline_point WHERE id_article=? and point_type=? ORDER BY id DESC',
                       (id_article,'update_time',))
        res = self.c.fetchone()
        if res is not None:
            res = res[1]
            dt_old = ScraperHelper.ScraperHelper().from_fake_datetime_to_datetime(res)
            dt_new = ScraperHelper.ScraperHelper().from_fake_datetime_to_datetime(last_update_time_found)
            if (dt_new is not None) and (dt_old is not None):
                if (dt_new - dt_old).total_seconds() > 0:
                    sql = """
                    INSERT INTO timeline_point
                    (
                        time,
                        point_type,
                        id_article
                    )
                    VALUES (?,?,?)
                    """
                    sql_args = (dt_new,'update_time', id_article)
                    self.c.execute(sql, sql_args)
                    self.conn.commit()

    def update_last_fetch_timeline_point(self, article_url, last_fetch_time):
        id_article = self.get_article_id_from_database(article_url)
        # Always update whithout checking the dates (because time always goes by since the last/former check...)
        self.c.execute('UPDATE timeline_point SET time=? WHERE point_type = ? AND id_article=?',
                       (last_fetch_time, 'last_fetch_time',id_article,))
        self.conn.commit()

    def create_themes_if_they_do_not_exist_then_link_article_with_themes(self, themes, article_url):
        for thm in themes:
            theme_id = self.get_theme_id_from_database(thm)
            if theme_id is None:
                sql = """
                    INSERT INTO theme
                    (
                        name
                    )
                    VALUES (?)
                    """
                sql_args = (thm,)
                self.c.execute(sql, sql_args)
                self.conn.commit()
                theme_id = self.get_theme_id_from_database(thm)
            id_article = self.get_article_id_from_database(article_url)
            self.insert_theme_article_jointure_in_database(theme_id, id_article)

    def log_article_to_database(self,
            id_newspaper, article_url, article_title, article_themes,
            article_creation_time, article_update_time, article_image_url):

        #Fetch time
        date_now = strftime("%Y-%m-%d %H:%M:%S") + strftime("%z")[:3] + ":" + strftime("%z")[3:]

        # If the article is already in the database, let's update the timeline
        if self.is_article_in_database(article_url):

            # Add an Update point if the 'article_update_time' passed if newer than the last update point date
            if (article_update_time is not  None) and (article_update_time != ''):
                self.add_a_timeline_point_update_if_needed(article_url, article_update_time)

            # (Always) update the Last fetch point
            self.update_last_fetch_timeline_point(article_url, date_now)

        # Else, the article has not been discovered until now
        else:

            if (article_creation_time is None) or (article_creation_time == ''):
                article_creation_time = date_now

            # Save the article
            self.insert_article_in_database(article_title,article_url,article_image_url, id_newspaper)
            id_article = self.get_article_id_from_database(article_url)

            if id_article is not None:

                sc = ScraperHelper.ScraperHelper()
                # Create a timeline point (article creation)
                self.insert_timeline_point_in_database(sc.from_fake_datetime_to_datetime(article_creation_time), 'creation_time', id_article)

                if (article_update_time is not  None) and (article_update_time != ''):
                    # Add a timeline point (article last update)
                    self.insert_timeline_point_in_database(sc.from_fake_datetime_to_datetime(article_update_time), 'update_time', id_article)

                # Create a timeline point (article last fetch)
                self.insert_timeline_point_in_database(sc.from_fake_datetime_to_datetime(date_now), 'last_fetch_time', id_article)

                # Record the themes involved
                self.create_themes_if_they_do_not_exist_then_link_article_with_themes(article_themes, article_url)

    def close_connection(self):
        self.conn.close()
