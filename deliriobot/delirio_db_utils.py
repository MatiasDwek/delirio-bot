from collections import namedtuple

from deliriobot.exceptions.no_such_element_error import *
from deliriobot.db_utils import *
from deliriobot.config import *

__con__ = db_connect()
__cur__ = __con__.cursor()

def save_user(username):
    query = 'SELECT EXISTS(SELECT 1 FROM users WHERE username=? collate NOCASE) LIMIT 1'
    check = __cur__.execute(query, [username])
    if check.fetchone()[0] == 0:
        username_sql = 'INSERT INTO users (username) VALUES (?)'
        __cur__.execute(username_sql, [username])
        __con__.commit()

def save_subreddit(subreddit):
    query = 'SELECT EXISTS(SELECT 1 FROM subreddits WHERE name=?) LIMIT 1'
    check = __cur__.execute(query, [subreddit])
    if check.fetchone()[0] == 0:
        post_sql = 'INSERT INTO subreddits (name) VALUES (?)'
        __cur__.execute(post_sql, [subreddit])
        __con__.commit()

def save_post(post):
    query = 'SELECT EXISTS(SELECT 1 FROM posts WHERE id=?) LIMIT 1'
    check = __cur__.execute(query, [post.id])
    if check.fetchone()[0] == 0:
        post_sql = 'INSERT INTO posts (id, url, title, subreddit) VALUES (?, ?, ?, ?)'
        __cur__.execute(post_sql, post)
        __con__.commit()

def save_request(comment, reddit):
    save_user(comment.author.name)
    save_subreddit(comment.subreddit.display_name)

    Post = namedtuple('Post', 'id url title subreddit')
    post = Post(comment.link_id, comment.link_permalink, reddit.submission(id=comment.link_id[3:]).title, comment.subreddit.display_name)
    save_post(post)

    query = 'SELECT EXISTS(SELECT 1 FROM comments WHERE id=?) LIMIT 1'
    check = __cur__.execute(query, [post.id])
    if check.fetchone()[0] == 0:
        comment_sql = 'INSERT INTO comments (id, url, date, content, user, parent, parent_post, should_reply) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        should_reply = 'IGNORE' if comment.author.name == DELIRIO_CONFIG['bot_name'] else 'TRUE' # avoid replying to the bot itself, some response may contain the call keyword
        __cur__.execute(comment_sql, (comment.name, comment.permalink, comment.created_utc, comment.body, comment.author.name, comment.parent_id, comment.link_id, should_reply))
        __con__.commit()
    return

def set_comment_should_reply(comment_id, state):
    if not ('TRUE', 'FALSE', 'IGNORE').__contains__(state):
        raise ValueError('State must be either TRUE, FALSE or IGNORE')

    query = 'SELECT EXISTS(SELECT 1 FROM comments WHERE id=?) LIMIT 1'
    check = __cur__.execute(query, [comment_id])
    if check.fetchone()[0] == 0:
        raise NoSuchElementError('No comment with id {} found'.format(comment_id))
    query = 'UPDATE comments SET should_reply = \'{}\' WHERE id=?'.format(state)
    __cur__.execute(query, [comment_id])
    __con__.commit()

def validate_request(comment):
    # Check if the user is posting requests too often
    query = "SELECT MAX(date) FROM comments WHERE user = ? AND should_reply <> \'TRUE\'"
    __cur__.execute(query, (comment.author.name,))
    last_user_request_date = __cur__.fetchone()[0]
    if last_user_request_date is None:
        last_user_request_date = 0
    delta_time = comment.created_utc - last_user_request_date
    if delta_time < DELIRIO_CONFIG['user_wait_time']:
        return False

    # Check if the post title contains a serious tag
    __cur__.execute('SELECT title FROM posts WHERE id = ?', (comment.link_id,))
    post_title = __cur__.fetchone()[0]
    serious_tags = DELIRIO_CONFIG['ignored_tags']
    serious_tags_lower = [x.lower() for x in serious_tags]
    if any(x in post_title.lower() for x in serious_tags_lower):
        return False

    return True
