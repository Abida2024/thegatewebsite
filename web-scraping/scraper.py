# This file servers as skeleton code for scraping down all articles 
# from The Gate's backend and storing it in a SQLite table

# This is a common Python library for web-scraping
from bs4 import BeautifulSoup 
import requests
import urllib.request
import re
import os
import lxml
from datetime import datetime

# For user-pass
import mechanize 
import http.cookiejar

from create_sqlite_table import Gate

import html

class Scraper:
    def __init__(self, url):
        # Base admin page for the Gate
        self.base_url = url
        # Make the connection to the sqlite database
        self.db = Gate()

    def authentication(self, login_url):
        ''' As the website is password protected, we need to supply 
        both our userpass and our csrf token '''
        # https://stackoverflow.com/questions/65701658/why-is-this-login-csrf-verification-failing-im-able-to-get-the-key
        head = { 
            'Content-Type':'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
            # 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        # Cookies
        self.s = requests.session()
        r = self.s.get(login_url)
        csrftoken = self.s.cookies['csrftoken'] # token 
        cookies = r.cookies # pages cookies to preserve when we go from one page to the next

        # Set CSRF-Token
        head['X-CSRF-Token'] = csrftoken
        head['X-Requested-With'] = 'XMLHttpRequest'
        head['Referer'] = login_url

        payload = {
        'username':'abidaasker',
        'password':'ucgate20',
        'csrfmiddlewaretoken' : csrftoken,
        }

        self.s.post(login_url, data=payload, headers = head)
        print("Successfully authenticated!")
    
    def load_url(self, url):
        ''' Load the url and grab all the html text ''' 
        # Try to get a page behind the login page
        index_page = self.s.get(url)
        soup = BeautifulSoup(index_page.text, 'html.parser')
        return soup
    
    def scrape_articles(self):
        ''' Scrape all the articles for the first 25 pages '''
        article_count = 0
        # 25 pages worth of articles, each page has 51-52 articles
        for i in range(1, 27):
            url = self.base_url+'pages/4/?p='+str(i)
            soup_i = self.load_url(url)
            articles_soup = soup_i.find('tbody').find_all('tr')
            # scrape all the articles on the given page
            for article in articles_soup:
                article_url = 'http://uchicagogate.com'+article.find('a')['href']
                article_soup = self.load_url(article_url)
                if self.scrape_insert_article(article_soup, article_url):
                    print(article_count)
                    article_count += 1
                    return

        print("Successfully scraped {count} articles out of 1251".format(count=article_count))
                            
    def scrape_insert_article(self, soup, article_url):
        '''' Scrape content and relevant metadata of an article 
        and insert into the database ''' 
        # Retrieve the relevant content: title, contributor, 
        # category, image_url, featured_image_caption, lede, body
        objects = soup.find('ul', {'class': 'objects'})
        # title 
        title_li = objects.find('li', {'class': 'object full title required char_field'})
        title = title_li.find('input')['value']
        # classification
        classification_li = objects.find_all('li', {'class': 'object collapsible multi-field'})[0]
        # get all the contributors 
        contributors_li = classification_li.find('select', {'id': 'id_contributors'}).find_all('option')
        contributors = []
        for contributor in contributors_li:
            contributors.append(contributor.text.strip())
        # get all the categories 
        categories_li = classification_li.find('ul', {'id': 'id_categories-FORMS'}).select('option[selected]')
        categories = []
        for category in categories_li:
            categories.append(category.text.strip())
        # feature_image
        image_li = objects.find_all('li', {'class': 'object collapsible multi-field'})[1]
        image_field = image_li.find('ul', {'class': 'actions'})
        image_url = ""
        if image_field is not None: 
            image_url = image_field.find('a')['href']
        # image caption 
        image_caption = image_li.find('li', {'class': 'char_field'}).find('div', {'class': 'input'}).text.strip()
        # lede
        lede_li = objects.find('li', {'class': 'object required char_field'})
        lede = lede_li.find('div', {'class': 'input'}).find('textarea').text.strip()
        # body 
        body_li = objects.find('li', {'class': 'object required block_field stream-field'})
        body = body_li.find('div', {'class': 'input'})

        # TODO: Date Published
        # remove the edit 
        base_url = article_url[:article_url.rindex("/", 0, -1)+1]
        base_soup = self.load_url(base_url)
        date = base_soup.find('div', {'class': 'human-readable-date'})['title']
        datetime_str = datetime.strptime(date, '%d %b %Y %H:%M')
        # TODO: SEO fields? 

        params = {
            'title': title, 
            'contributors': str(contributors), 
            'category': str(categories), 
            'image_url': image_url,
            'featured_image_caption': image_caption, 
            'lede': lede, 
            'body': str(body), 
            'date': datetime_str
        }
        self.db.add_new_articles(params)
        return True
    
if __name__ == "__main__":
    scraper = Scraper(url='http://uchicagogate.com/admin/')
    login_url = 'http://uchicagogate.com/admin/login/?next=/admin/'
    scraper.authentication(login_url)
    scraper.load_url('http://uchicagogate.com/admin/')
    scraper.scrape_articles()