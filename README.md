# thegatewebsite

Welcome! We'll primarily be using this repo to store the scripts used to scrape down The Gate's historic websites, with the rest of the website migraton happening through Wordpress.

# Step 1. Scraping Down Historic Files Using Beautiful Soup

## What is web scraping?

Web scraping is technique used to extract data from a website --
for example, you may wish to extract all the text on a page, download all the images, grab all the links on a given article, etc!

We can use web scraping to extract different elements from an
HTML document. For example, we could grab the title from the following element.

`<div class="article_title"> This is a sample article title </div> `

## What is Beautiful Soup?

Beautiful Soup is a popular Python library used for web-scraping -- another popular option is Selenium.

Here is the documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

As well as some introductory tutorials that can likely explain this much
better than I can:

[1] https://realpython.com/beautiful-soup-web-scraper-python/

[2] https://www.youtube.com/watch?v=XQgXKtPSzUI

### Important Stuff for our context

After connecting to a page using the _requests_ module, we can
extract all the HTML on a given page using `BeautifulSoup(sample_page.text, 'html.parser')`

The 'soup' contains the entire HTML content of the page.

```
def load_url(self, url):
    ''' Load the url and grab all the html text '''
    # Try to get a page behind the login page
    index_page = self.s.get(url)
    soup = BeautifulSoup(index_page.text, 'html.parser')
    return soup
```

To extract certain elements we can use the _find_ or _find_all_ methods:

In the example, below, we get the first instance of a _ul_ element whose
class attribute is equal to _objects_. We could also pass in different
attributes such as `{'id': 'sample_id'}`. We could also use _find_all_ to grab a list of all elements.

```
objects = soup.find('ul', {'class': 'objects'})
```

What is returned is everything from the beginning to the end of each element:

```
<ul class='objects>
EVERYTHING IN BETWEEN
</ul>
```

## A Summary of the scraper.py file

Our goal is to scrape the following information for each article:
title, contributors, category, image_url, featured_image_caption, lede, body, and the date published. We then want to store all this information in a database.

Note: There may be other fields we want to scrape pertaining to
search-engine optimization (SEO).

### SQLite

SQLite is a database that comes preinstalled if you have python, and sqlite3
is a popular library used to interact with this database.

In `create_sqlite_table.py`, I've used the following command to create the
table gate_articles in the thegate.db database.

```
CREATE TABLE IF NOT EXISTS
    gate_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        contributors TEXT,
        category TEXT,
        image_url TEXT,
        featured_image_caption TEXT,
        lede TEXT NOT NULL,
        body TEXT NOT NULL,
        date TIMESTAMP
    )
```

### Scraping Relevant Attributes

I've looked through the HTML document using inspect to identify
where each relevant field of an article is located, the function
might look long and complicated, but really it's just a matter of identifying
where everything is located on the HTML document.

```
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
    date_div = base_soup.find('div', {'class': 'human-readable-date'})
    datetime_str = None
    if date_div is not None:
        date = date_div['title']
        datetime_str = datetime.strptime(date, '%d %b %Y %H:%M')
    else:
        print("No date!")
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
```

### Running the file and connecting to the SQLite Database

Note: You will not need to run the file as all the
articles have already been inserted into the SQLite Database.

To run the file, make sure you have Python installed
and simply run the following from your terminal:

`python3 webscraper.py`

To connect to the database thegate.db, run
the following from the terminal:

`sqlite3 thegate.db`

Once you're in the SQLite Command Line Interface,
you can check the tables the database, as well as
submit SQL queries:

```
>> .tables
>> SELECT * FROM gate_articles;
```

# Step 2. Wordpress Website Re-Design

I've looked through a few free wordpress templates that would be good for a student publication like The Gate. I've tentatively settled on the _Canard_ template, although we can feel free to switch it up with some other templates.

Take a look at the documentation below:

WordPress Canard Theme: https://wordpress.com/theme/canard/thegateuchicago.wordpress.com

# Step 3. Wordpress Extension to Upload Files

We'll be using the WordPress REST API to post old articles from The Gate's
current website.

Take a look at the documentation here:
https://developer.wordpress.org/rest-api/
