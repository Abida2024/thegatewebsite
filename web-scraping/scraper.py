# This file servers as skeleton code for scraping down all articles 
# from The Gate's backend and storing it in a SQLite table

# This is a common Python library for web-scraping
from bs4 import BeautifulSoup 
import requests
import urllib.request
import re
import os
import lxml

# For user-pass
import mechanize 
import http.cookiejar

from create_sqlite_table import Gate

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
        for i in range(1, 26):
            url = self.base_url+'pages/4/?p='+str(i)
            soup_i = self.load_url(url)
            articles_soup = soup_i.find('tbody').find_all('tr')
            # scrape all the articles on the given page
            for article in articles_soup:
                article_url = 'http://uchicagogate.com'+article.find('a')['href']
                article_soup = self.load_url(article_url)
                if self.scrape_insert_article(article_soup):
                    article_count += 1
        print("Successfully scraped {count} articles out of 1947".format(count=article_count))
                            
    def scrape_insert_article(self, soup):
        '''' Scrape content and relevant metadata of an article 
        and insert into the database ''' 
        # Retrieve the relevant content: title, contributor, 
        # category, image_url, featured_image_caption, lede, body
        fields = soup.find_all('div', {'class': 'input'})
        # title 
        title = fields[0].find('input')['value']
        # contributors 
        contributors = fields[1].find('select').find('option').next
        # image_url: links to /admin/images/990/
        # image_url = fields[2].find('ul', {'class': 'actions'}).find('a')['href']
        # lede = fields[4].find('textarea', {'id': 'id_lede'}).next
        # body is stored as html
        body = fields[5].find('textarea', {'id': 'body-0-value'}).next

        # NOTE: There is probably a better way to do this lol, but 
        # some of these fields have embedded Javascript, so we're looking at the preview instead
        # TODO: Identify multiple contributors 
        # TODO: SEO fields? 

        # preview 
        # preview_soup = self.load_url('http://uchicagogate.com/admin/pages/1947/edit/preview/')
        # category = preview_soup.find('div', {'class': 'kicker'}).find('a')['href']
        # date = preview_soup.find('span', {'class': 'timestamp subheader'})
        # image_caption = preview_soup.find('figure').find('figcaption').next

        params = {
            'title': title, 
            'contributors': contributors, 
            'category': None, 
            'image_url': None,
            'featured_image_caption': None, 
            'lede': None, 
            'body': body, 
            'date': None
        }
        print(params)
        # self.db.add_new_articles(params)

        return True
    
if __name__ == "__main__":
    scraper = Scraper(url='http://uchicagogate.com/admin/')
    login_url = 'http://uchicagogate.com/admin/login/?next=/admin/'
    scraper.authentication(login_url)
    scraper.load_url('http://uchicagogate.com/admin/')
    scraper.scrape_articles()