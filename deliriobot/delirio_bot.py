#!/usr/bin/python
import praw
import re
import random
from deliriobot.db_utils import *

reddit = praw.Reddit('delirio-bot')

subreddit = reddit.subreddit("pythonforengineers")

while True:
    for comment in subreddit.stream.comments():
        save_request(comment)
        print(type(comment.subreddit.display_name))
        if re.match("!delirio", comment.body, re.IGNORECASE):
            pass
            # if (validate_request(comment)):
            #     print("a delirio image")