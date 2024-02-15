# This script uses the wordpress rest api to upload old articles
import requests
import base64
import json

from webscraping.create_sqlite_table import Gate

from bs4 import BeautifulSoup

API_URL = 'https://thegateuchicago.wpcomstaging.com/wp-json/wp/v2'

def authentication():
    wordpress_user = 'thegateuchicago@gmail.com'
    wordpress_password = 'Aerl wOuu 5uOs DxCr crx4 6jbw'
    wordpress_credentials = f"{wordpress_user}:{wordpress_password}"
    wordpress_token = base64.b64encode(wordpress_credentials.encode('utf-8'))
    wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}
    return wordpress_header 

def upload_image(image_path, caption, wordpress_header):
    # To-Do: Open the correct images
    image_data = open('elasticsearch.png', 'rb')
    data = {
        'caption': caption, 
        'file': image_data
    }
    response = requests.post(f'{API_URL}/media', headers=wordpress_header, files=data)
    if response.status_code == 201:
        return response.json()['id']
    else:
        print("Failed to upload image. Status code:", response.status_code)
        print("Response:", response.text)
        return None

def create_wordpress_post(params, wordpress_header):
    api_url = f'{API_URL}/posts'
    # use bs to get everything in the text area 
    soup = BeautifulSoup(params['content'], 'html.parser')
    content = soup.find('textarea').next
    # params['category'].replace('', '"')
    print(params['image_url'])
    data = {
    'title' : params['title'],
    'status': 'publish',
    'content': content, 
    'category': '1,2'
    }
    print(params['category'])
    # Not all the 
    featured_image_id = upload_image(params['image_url'], params['featured_image_caption'], wordpress_header)
    if featured_image_id:
        data['featured_media'] = featured_image_id
    response = requests.post(api_url,headers=wordpress_header, json=data)
    print(response)

def upload_articles(wordpress_header):
    db = Gate()
    rows = db.read_articles()
    for i, article in enumerate(rows):
        if i == 1:
            break
        params = {
            "title": article[1], 
            "contributors": article[2], 
            "category": article[3], 
            "image_url": article[4], 
            "featured_image_caption": article[5], 
            "lede": article[6],
            "content": article[7], 
            "date": article[8]
        }
        create_wordpress_post(params, wordpress_header)
        
if __name__=="__main__":
    wordpress_header = authentication()
    upload_articles(wordpress_header)
    # create_wordpress_post(wordpress_header)