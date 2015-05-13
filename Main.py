# coding: utf-8
from __future__ import unicode_literals
import datetime
from app.newspapers.fr import *

newspapers_fr = []

newspapers_fr.append(LeMonde.Scrapper())
newspapers_fr.append(LeFigaro.Scrapper())
newspapers_fr.append(VingtMinutes.Scrapper())
newspapers_fr.append(MetroNews.Scrapper())
newspapers_fr.append(DirectMatin.Scrapper())
newspapers_fr.append(Lequipe.Scrapper())
newspapers_fr.append(LeParisien.Scrapper())
newspapers_fr.append(Lexpress.Scrapper())
newspapers_fr.append(Liberation.Scrapper())
newspapers_fr.append(LesEchos.Scrapper())
newspapers_fr.append(OuestFrance.Scrapper())
newspapers_fr.append(Challenges.Scrapper())
newspapers_fr.append(TF1.Scrapper())

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
