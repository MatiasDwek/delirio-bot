from deliriobot.db_utils import db_connect

__con__ = db_connect() # connect to the database
__cur__ = __con__.cursor() # instantiate a cursor obj

users_sql = """
CREATE TABLE users (
  username text PRIMARY KEY,
  UNIQUE (username COLLATE NOCASE))"""
__cur__.execute(users_sql)

subreddits_sql = """
CREATE TABLE subreddits (
  name text PRIMARY KEY,
  UNIQUE (name COLLATE NOCASE))"""
__cur__.execute(subreddits_sql)

posts_sql = """  
CREATE TABLE posts (
  id text PRIMARY KEY,
  url text NOT NULL,
  title text NOT NULL,
  subreddit text NOT NULL,
  FOREIGN KEY (subreddit) REFERENCES name (subreddits))"""
__cur__.execute(posts_sql)

comments_sql = """
CREATE TABLE comments (
  id text PRIMARY KEY,
  url text NOT NULL,
  date real NOT NULL,
  content text NOT NULL,
  user text NOT NULL,
  parent text NOT NULL,
  parent_post text NOT NULL,
  should_reply text CHECK(should_reply IN ('TRUE','FALSE','IGNORE')) NOT NULL DEFAULT 'TRUE',
  FOREIGN KEY (user) REFERENCES users (username),
  FOREIGN KEY (parent_post) REFERENCES posts (id))"""
__cur__.execute(comments_sql)