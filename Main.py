# coding: utf-8
from __future__ import unicode_literals
import datetime
from app.newspapers.fr import *

newspapers_fr = []

newspapers_fr.append(LeMonde.Scraper())
newspapers_fr.append(LeFigaro.Scraper())
newspapers_fr.append(VingtMinutes.Scraper())
newspapers_fr.append(MetroNews.Scraper())
newspapers_fr.append(DirectMatin.Scraper())
newspapers_fr.append(Lequipe.Scraper())
newspapers_fr.append(LeParisien.Scraper())
newspapers_fr.append(Lexpress.Scraper())
newspapers_fr.append(Liberation.Scraper())
newspapers_fr.append(LesEchos.Scraper())
newspapers_fr.append(OuestFrance.Scraper())
newspapers_fr.append(Challenges.Scraper())
newspapers_fr.append(TF1.Scraper())

# Start fetching
print '--------------------------------------------------------------------------------'
script_start_time = datetime.datetime.now()
print 'Started fetch script ( timestamp :', script_start_time, ')'

for paper in newspapers_fr:
    try:
        paper.start_scrapping_articles_found_on_homepage()
    except:
        print '[ERR] An error occurred when fetching ', paper.name, '( timestamp :', datetime.datetime.now(), ')'

script_end_time = datetime.datetime.now()
elapsed_time = script_end_time - script_start_time
print 'Fetch script ended ( timestamp :', script_end_time, \
      ', took %s min, %s sec' % divmod(elapsed_time.days * 86400 + elapsed_time.seconds, 60), ')'
