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
newspapers_fr.append(LaTribune.Scraper())
newspapers_fr.append(Capital.Scraper())
newspapers_fr.append(NouvelObs.Scraper())
newspapers_fr.append(LaCroix.Scraper())
newspapers_fr.append(Lhumanite.Scraper())
newspapers_fr.append(Europe1.Scraper())
newspapers_fr.append(ValeursActuelles.Scraper())
newspapers_fr.append(BFMTV.Scraper())
newspapers_fr.append(FranceInter.Scraper())

# Start fetching
print '--------------------------------------------------------------------------------'
script_start_time = datetime.datetime.now()
print 'Started fetch script ( timestamp :', script_start_time, ')'

for paper in newspapers_fr:
    paper_start_time = datetime.datetime.now()
    try:
        paper.start_scrapping_articles_found_on_homepage()
    except:
        print "[ERR] An error occurred when fetching %s (timestamp : %s)" % (paper.name, datetime.datetime.now())
    paper_end_time = datetime.datetime.now()
    elapsed_paper_time = paper_end_time - paper_start_time
    print "[INFO] " + paper.name + " fetch complete ( timestamp : %s, took %s min, %s sec )"\
      % ((paper_end_time,) + divmod(elapsed_paper_time.days * 86400 + elapsed_paper_time.seconds, 60))

script_end_time = datetime.datetime.now()
script_elapsed_time = script_end_time - script_start_time
print "Fetch script ended ( timestamp : %s, took %s min, %s sec )"\
      % ((script_end_time,) + divmod(script_elapsed_time.days * 86400 + script_elapsed_time.seconds, 60))
