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
                title TEXT,
                contributors TEXT, 
                category TEXT, 
                image_url TEXT,
                featured_image_caption TEXT,
                lede TEXT,
                body TEXT NOT NULL, 
                date TEXT
                )
                ''')
        # Note to self: We may need to add more metadata columns (there are 
        # some SEO columns in the current backend)
        self.conn.commit()
    
    def add_new_articles(self, params):
        ''' Adds a new article with all relevant metadata into the 
        gate_articles table '''
        params = (
            params['title'], 
            params['contributors'], 
            params['category'], 
            params['image_url'], 
            params['featured_image_caption'], 
            params['lede'],
            params['body'], 
            params['date']
            )
        sql = '''INSERT INTO student_courses VALUES (NULL,?,?,?,?,?,?,?,?,?)'''
        self.curr.execute(select_statement, params)
        self.conn.commit()



