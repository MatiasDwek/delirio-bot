from collections import namedtuple
import logging
import os
import sqlite3

from deliriobot.exceptions.no_such_element_error import *
from deliriobot.config import *

class Database:

    def __init__(self):
        # create a default path to connect to and create (if necessary) a database
        # called 'database.sqlite3' in the same directory as this script
        db_path = os.path.join(os.path.dirname(__file__), Config.DATABASE_PATH)
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
    
    def save_user(self, username):
        query = 'SELECT EXISTS(SELECT 1 FROM users WHERE username=? collate NOCASE) LIMIT 1'
        check = self.cur.execute(query, [username])
        if check.fetchone()[0] == 0:
            username_sql = 'INSERT INTO users (username) VALUES (?)'
            self.cur.execute(username_sql, [username])
            self.con.commit()
            logging.info('Saved user {}'.format(username))
    
    def save_subreddit(self, subreddit):
        query = 'SELECT EXISTS(SELECT 1 FROM subreddits WHERE name=?) LIMIT 1'
        check = self.cur.execute(query, [subreddit])
        if check.fetchone()[0] == 0:
            post_sql = 'INSERT INTO subreddits (name) VALUES (?)'
            self.cur.execute(post_sql, [subreddit])
            self.con.commit()
            logging.info('Saved subreddit {}'.format(subreddit))
    
    def save_post(self, post):
        query = 'SELECT EXISTS(SELECT 1 FROM posts WHERE id=?) LIMIT 1'
        check = self.cur.execute(query, [post.id])
        if check.fetchone()[0] == 0:
            post_sql = 'INSERT INTO posts (id, url, title, subreddit) VALUES (?, ?, ?, ?)'
            self.cur.execute(post_sql, post)
            self.con.commit()
            logging.info('Saved post {}'.format(post.id))
    
    def save_request(self, comment, reddit):
        self.cur.execute("SELECT count(*) FROM comments WHERE id = ?", (comment.name,))
        if self.cur.fetchone()[0] != 0:
            # the request was already saved
            return

        self.save_user(comment.author.name)
        self.save_subreddit(comment.subreddit.display_name)
    
        Post = namedtuple('Post', 'id url title subreddit')
        post = Post(comment.link_id, comment.link_permalink, reddit.submission(id=comment.link_id[3:]).title, comment.subreddit.display_name)
        self.save_post(post)
    
        query = 'SELECT EXISTS(SELECT 1 FROM comments WHERE id=?) LIMIT 1'
        check = self.cur.execute(query, [post.id])
        if check.fetchone()[0] == 0:
            comment_sql = 'INSERT INTO comments (id, url, date, content, user, parent, parent_post, should_reply) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            should_reply = 'IGNORE' if comment.author.name == Config.BOT_NAME else 'TRUE' # avoid replying to the bot itself, some response may contain the call keyword
            self.cur.execute(comment_sql, (comment.name, comment.permalink, comment.created_utc, comment.body, comment.author.name, comment.parent_id, comment.link_id, should_reply))
            self.con.commit()
            logging.info('Saved request {}'.format(comment.name))
    
    def get_comment_state(self, comment_id):
        self.cur.execute('SELECT should_reply FROM comments WHERE id = ?', (comment_id,))
        return self.cur.fetchone()[0]
    
    def set_comment_state(self, comment_id, state):
        if not ('TRUE', 'FALSE', 'IGNORE').__contains__(state):
            raise ValueError('State must be either TRUE, FALSE or IGNORE')
    
        query = 'SELECT EXISTS(SELECT 1 FROM comments WHERE id=?) LIMIT 1'
        check = self.cur.execute(query, [comment_id])
        if check.fetchone()[0] == 0:
            raise NoSuchElementError('No comment with id {} found'.format(comment_id))
    
        query = 'UPDATE comments SET should_reply = \'{}\' WHERE id=?'.format(state)
        self.cur.execute(query, [comment_id])
        self.con.commit()
        logging.info('Set comment {0} should reply state to {1}'.format(comment_id, state))
    
    def validate_request(self, comment):
        # Check if the user is posting requests too often
        query = "SELECT MAX(date) FROM comments WHERE user = ? AND should_reply <> \'TRUE\'"
        self.cur.execute(query, (comment.author.name,))
        last_user_request_date = self.cur.fetchone()[0]
        if last_user_request_date is None:
            last_user_request_date = 0
        delta_time = comment.created_utc - last_user_request_date
        if delta_time < Config.USER_WAIT_TIME:
            logging.info('Request {} refused due to querying too often'.format(comment.link_id))
            return False
    
        # Check if the post title contains an ignore tag
        self.cur.execute('SELECT title FROM posts WHERE id = ?', (comment.link_id,))
        post_title = self.cur.fetchone()[0]
        serious_tags = Config.IGNORED_TAGS
        serious_tags_lower = [x.lower() for x in serious_tags]
        if any(x in post_title.lower() for x in serious_tags_lower):
            logging.info('Request {} refused due post being ignored'.format(comment.link_id))
            return False
    
        return True
