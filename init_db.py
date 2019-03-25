from db_utils import db_connect
con = db_connect() # connect to the database
cur = con.cursor() # instantiate a cursor obj

users_sql = """
CREATE TABLE users (
    username text PRIMARY KEY"""
cur.execute(users_sql)

posts_sql = """
CREATE TABLE posts (
    id integer PRIMARY KEY,
    url text NOT NULL"""
cur.execute(posts_sql)

comment_sql = """
CREATE TABLE posts (
    id integer PRIMARY KEY,
	url text NOT NULL,
    date text,
	content text NOT NULL,
	user text NOT NULL,
    parent_user text NOT NULL,
	FOREIGN KEY (user) REFERENCES users (username)),
    FOREIGN KEY (parent_user) REFERENCES users (username))"""
cur.execute(comment_sql)