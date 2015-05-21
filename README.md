# Newspapers Scraper

**Newspapers Scraper** is a Python script that allows you to keep track of articles from newspapers.

## Setup

To start using the script :

1) Install `pip` ([Source](https://pip.pypa.io/en/latest/installing.html)) :


    $ python https://bootstrap.pypa.io/get-pip.py
    
2) Install required packages :


    $ pip install requests beautifulsoup4
    
3) Configuration :

* Rename `Config.py.sample` to `Config.py`.
* Open up the `Config.py` file and replace the `database_path` and the `database_file_name` by what you want.

4) Create a new cronjob :

Edit scheduled tasks ("cronjobs") :

    $ crontab -e

Add this line at the bottom to scrap articles every 30 minutes :

    */30 * * * * /usr/bin/python /path/to/Scraper/Main.py

Save, and quit. That's all.

## Overview

* `Main.py` : script entry point
* `app/Config.py` : config
* `app/utils/Database.py` : connection to the sqlite3 database
* `app/utils/ScraperHelper.py` : very (few) basic helper functions
* `app/newspapers/[language]/[newspaper].py` : the newspaper's articles Scrapers

## FAQ

Q. Why not using RSS for grabbing articles' urls ?

A. For most newspapers, no RSS feed was available.

Q. Which articles are kept or not kept ?

A. Here is the rule of thumb :

* The Scraper only keeps track of the articles displayed on the newspapers' homepages
* The premium/restricted articles are never retained
* The ads are never retained
* The blog posts are never retained

Q. Are HTTP requests async ?

A. No, the HTTP calls are synchronous.

Q. Are HTTP requests 404-tolerant ?

A. No.

Q. Is the code dirty ?

A. Yes.


## License

Copyright (c) 2015, protoop. All rights reserved.

* BeautifulSoup is released under terms of MIT License. [Documentation](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* Requests is released under terms of Apache2 License. [Documentation](http://docs.python-requests.org/en/latest/)
