# db_utils.py
import os  
import sqlite3

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

def db_connect(db_path=DEFAULT_PATH):  
    con = sqlite3.connect(db_path)
    return con

def save_user(username):
    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM users WHERE username=? collate NOCASE) LIMIT 1'
    check = cur.execute(query, [username])
    if check.fetchone()[0] == 0:
        username_sql = 'INSERT INTO users (username) VALUES (?)'
        cur.execute(username_sql, [username])
        con.commit()

def save_post(post):
    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM posts WHERE id=?) LIMIT 1'
    check = cur.execute(query, [post.id])
    if check.fetchone()[0] == 0:
        post_sql = 'INSERT INTO posts (id, url) VALUES (?, ?)'
        cur.execute(post_sql, post)
        con.commit()

def save_request(comment):
    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM users WHERE username=? collate NOCASE) LIMIT 1'
    check = cur.execute(query, comment.author.name)
    if check.fetchone()[0] == 0:
        save_user(comment.author.name)

    print(comment.body)
    print(comment.author.name)
    print(comment.permalink)
    print(comment.link_permalink)
    print(comment.name)
    print(comment.parent_id)
    return

def validate_request(comment):
    return True
