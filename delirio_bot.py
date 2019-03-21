#!/usr/bin/python
import praw
import re
import random

reddit = praw.Reddit('delirio-bot')

subreddit = reddit.subreddit("argentina")

for comment in subreddit.stream.comments():
    print(comment.body)
