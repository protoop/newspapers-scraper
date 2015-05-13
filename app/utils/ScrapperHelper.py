# coding: utf-8
from __future__ import unicode_literals
import datetime

import requests
from bs4 import BeautifulSoup
import pytz

from app import Config


class ScrapperHelper:

    def __init__(self):
        config = Config.Config()
        self.user_agent = config.get_user_agent()

    def getSoupFromPage(self, page_url, encoding='utf-8'):
        r = requests.get(page_url, headers=self.user_agent)
        # encoding : usually 'utf-8' (default) or 'ISO-8859-1'
        r.encoding = encoding
        if unicode(r.status_code).startswith('4') or unicode(r.status_code).startswith('5'):
            return ''
        else:
            soup = BeautifulSoup(r.text)
            return soup

    def from_fake_datetime_to_datetime(self, dt):
        tz = pytz.timezone('Europe/Paris')
        if(dt is not None) and (dt != '') and (type(dt) != 'datetime.datetime') and len(dt)> 10:
            return tz.localize(datetime.datetime(int(dt[0:4]),int(dt[5:7]),int(dt[8:10]),
                                 int(dt[11:13]),int(dt[14:16]),int(dt[17:19])))
        elif(dt is not None) and (dt != '') and (type(dt) != 'datetime.datetime') and len(dt)==10:
            return tz.localize(datetime.datetime(int(dt[0:4]),int(dt[5:7]),int(dt[8:10])))
        else:
            return None
