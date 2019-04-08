#!/usr/bin/python
import praw
import re
import random
from deliriobot.db_utils import *
from deliriobot.validate import *

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

                validate_request(comment.name)
                cur.execute('SELECT should_reply FROM comments WHERE id=?', (comment.name,))
                if cur.fetchone()[0] == 'TRUE':
                    # Before posting reply, ask if the bot is posting replies too often
                    # Post reply
                    # After posting reply, save it in the db
                    print('The request reads {}'.format(comment.content))
                else:
                    print('I posted comment {}'.format(comment.name))