import sqlite3

class Gate: 
    def __init__(self):
        # Connect to the database thegate, and create it if it doesn't exist
        self.conn = sqlite3.connect("thegate.db")
        self.cur = self.conn.cursor()
        # Initialize the table gate_articles if DNE
        self.cur.execute('''CREATE TABLE IF NOT EXISTS
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
                ''')
        # Note to self: We may need to add more metadata columns (there are 
        # some SEO columns in the current backend)
        self.conn.commit()
    
    def add_new_articles(self, params):
        ''' Adds a new article with all relevant metadata into the 
        gate_articles table '''
        params = ({
            "title": params['title'], 
            "contributors": params['contributors'], 
            "category": params['category'], 
            "image_url": params['image_url'], 
            "featured_image_caption": params['featured_image_caption'], 
            "lede": params['lede'],
            "body": params['body'], 
            "date": params['date']
        })

        sql = '''INSERT INTO gate_articles VALUES 
            (NULL,
            :title,
            :contributors,
            :category,
            :image_url,
            :featured_image_caption,
            :lede,
            :body,
            :date)'''
        self.cur.execute(sql, params)
        self.conn.commit()
        # self.conn.close()



