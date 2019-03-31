#!/usr/bin/python
import praw
import re
import random
from deliriobot.db_utils import *

reddit = praw.Reddit('delirio-bot')

subreddit = reddit.subreddit("argentina")

for comment in subreddit.stream.comments():

    if re.match("!delirio", comment.body, re.IGNORECASE):
        pass
        # if (validate_request(comment)):
        #     print("a delirio image")