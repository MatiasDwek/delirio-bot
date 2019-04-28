from collections import namedtuple

from deliriobot.exceptions.no_such_element_error import *
from deliriobot.db_utils import *

def save_user(username):
    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM users WHERE username=? collate NOCASE) LIMIT 1'
    check = cur.execute(query, [username])
    if check.fetchone()[0] == 0:
        username_sql = 'INSERT INTO users (username) VALUES (?)'
        cur.execute(username_sql, [username])
        con.commit()

def save_subreddit(subreddit):
    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM subreddits WHERE name=?) LIMIT 1'
    check = cur.execute(query, [subreddit])
    if check.fetchone()[0] == 0:
        post_sql = 'INSERT INTO subreddits (name) VALUES (?)'
        cur.execute(post_sql, [subreddit])
        con.commit()

def save_post(post):
    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM posts WHERE id=?) LIMIT 1'
    check = cur.execute(query, [post.id])
    if check.fetchone()[0] == 0:
        post_sql = 'INSERT INTO posts (id, url, title, subreddit) VALUES (?, ?, ?, ?)'
        cur.execute(post_sql, post)
        con.commit()

def save_request(comment, reddit):
    save_user(comment.author.name)
    save_subreddit(comment.subreddit.display_name)

    Post = namedtuple('Post', 'id url title subreddit')
    post = Post(comment.link_id, comment.link_permalink, reddit.submission(id=comment.link_id[3:]).title, comment.subreddit.display_name)
    save_post(post)

    con = db_connect()
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT 1 FROM comments WHERE id=?) LIMIT 1'
    check = cur.execute(query, [post.id])
    if check.fetchone()[0] == 0:
        comment_sql = 'INSERT INTO comments (id, url, date, content, user, parent, parent_post, should_reply) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        should_reply = 'IGNORE' if comment.author.name == "DelirioBot" else 'TRUE'
        cur.execute(comment_sql, (comment.name, comment.permalink, comment.created_utc, comment.body, comment.author.name, comment.parent_id, comment.link_id, should_reply))
        con.commit()
    return

def set_comment_should_reply(comment_id, state):
    if not ('TRUE', 'FALSE', 'IGNORE').__contains__(state):
        raise ValueError('State must be either TRUE, FALSE or IGNORE')

    con = db_connect()
    cur = con.cursor()

    query = 'SELECT EXISTS(SELECT 1 FROM comments WHERE id=?) LIMIT 1'
    check = cur.execute(query, [comment_id])
    if check.fetchone()[0] == 0:
        raise NoSuchElementError('No comment with id {} found'.format(comment_id))
    query = 'UPDATE comments SET should_reply = \'{}\' WHERE id=?'.format(state)
    cur.execute(query, [comment_id])
    con.commit()

def validate_request(comment):
    con = db_connect()
    cur = con.cursor()
    query = "SELECT MAX(date) FROM comments WHERE user = ? AND should_reply <> \'TRUE\'"
    cur.execute(query, (comment.author.name,))
    last_user_request_date = cur.fetchone()[0]
    if last_user_request_date is None:
        last_user_request_date = 0
    delta_time = comment.created_utc - last_user_request_date
    if delta_time < 43200.0:
        return False
    else:
        return True
