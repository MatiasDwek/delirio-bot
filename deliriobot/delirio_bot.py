#!/usr/bin/python
import praw
import re
import random
from deliriobot.db_utils import *

properties = dict()
properties['answer_wait'] = 120.0 # 2 minutes
properties['user_wait'] = 43200.0 # 12 hours

reddit = praw.Reddit('delirio-bot')

subreddits = list()
subreddits.append(reddit.subreddit("pythonforengineers"))

con = db_connect()
cur = con.cursor()

while True:
    for subreddit in subreddits:
        for comment in subreddit.stream.comments():
            if re.match("!delirio", comment.body, re.IGNORECASE):
                cur.execute("SELECT count(*) FROM comments WHERE id = ?", (comment.name,))
                if cur.fetchone()[0] == 0:
                    save_request(comment)

                cur.execute('SELECT should_reply FROM comments WHERE id = ?', (comment.name,))
                if cur.fetchone()[0] == 'TRUE':
                    if validate_request(comment):
                        cur.execute("SELECT MAX(date) FROM comments WHERE should_reply = 'FALSE'")
                        last_comment_date = cur.fetchone()[0]
                        if last_comment_date is None:
                            last_comment_date = 0
                        delta_time = comment.created_utc - last_comment_date
                        # Before posting a reply, ask if the bot is posting replies too often
                        if delta_time > properties['answer_wait']:
                            # Post reply
                            print('Here goes the reply to comment {}'.format(comment.body))
                            # After posting reply, save it in the db
                    else:
                        cur.execute('UPDATE comments SET should_reply = \'IGNORE\' WHERE id=?', [comment.name])
                        con.commit()
                else:
                    print('The request from {} does not need a reply'.format(comment.name))