#!/usr/bin/python

import praw
import re
import random
import time

from deliriobot.comments_db_utils import *

properties = dict()
properties['answer_wait'] = 120.0  # 2 minutes (in seconds)
properties['user_wait'] = 43200.0  # 12 hours (in seconds)

wait_time = properties['answer_wait'] # (in seconds)

def random_line(file_name):
    file = open(file_name, mode="r", encoding="utf-8")
    line = next(file)
    for num, aline in enumerate(file, 2):
      if random.randrange(num): continue
      line = aline
    return line

def generate_reply():
    con_img = db_connect(os.path.join(os.path.dirname(__file__), 'images.sqlite3'))
    cur_img = con_img.cursor()
    cur_img.execute('SELECT * FROM images ORDER BY RANDOM() LIMIT 1') # Select random image from image database
    reply = "[{0}](https://i.imgur.com/{1})\n\n" \
            "&nbsp;\n" \
            "- - - - - -\n" \
            "^*DelirioBot* ^- " \
            "[^Source ^code](https://github.com/MatiasDwek/delirio-bot/tree/master/deliriobot)" \
            .format(random_line("../delirio-bot-data/replies.txt"), cur_img.fetchone()[0])

    return reply

def reply(comment):
    con = db_connect()
    cur = con.cursor()

    if validate_request(comment):
        cur.execute("SELECT MAX(date) FROM comments WHERE should_reply = 'FALSE'")
        last_comment_date = cur.fetchone()[0]
        if last_comment_date is None:
            last_comment_date = 0
        delta_time = comment.created_utc - last_comment_date
        # Before posting a reply, ask if the bot is posting replies too often
        global wait_time
        if delta_time > wait_time:
            # Post reply
            try:
                print('Here goes the reply to comment {}'.format(comment.body))
                comment.reply(generate_reply())
                cur.execute('UPDATE comments SET should_reply = \'FALSE\' WHERE id=?', [comment.name])
                con.commit()

                # Reset the default reply wait time
                wait_time = properties['answer_wait']
            except praw.exceptions.APIException as e:
                if e.error_type == 'RATELIMIT':
                    string_minutes = re.search(r'try again in (.*) minutes', e.message)
                    if string_minutes is None:
                        wait_time = 10 * 60 # wait for 10 minutes
                    else:
                        wait_time = (int(string_minutes.group(1)) + 1) * 60
                    print('bot is rate limited, waiting {} seconds'.format(wait_time))
    else:
        cur.execute('UPDATE comments SET should_reply = \'IGNORE\' WHERE id=?', [comment.name])
        con.commit()

def main():
    reddit = praw.Reddit('delirio-bot')

    # subreddits = ['Argentinacirclejerk', 'argentina', 'republicaargentina']
    subreddits = ['pythonforengineers']
    all_subreddits = reddit.subreddit('+'.join(subreddits))

    con = db_connect()
    cur = con.cursor()

    for comment in all_subreddits.stream.comments():
        # TODO sleep for a couple of seconds
        # time.sleep(5)
        if re.match("!delirio", comment.body, re.IGNORECASE):
            cur.execute("SELECT count(*) FROM comments WHERE id = ?", (comment.name,))
            if cur.fetchone()[0] == 0:
                save_request(comment, reddit)

            cur.execute('SELECT should_reply FROM comments WHERE id = ?', (comment.name,))
            if cur.fetchone()[0] == 'TRUE':
                reply(comment)
            else:
                print('The request from {} does not need a reply'.format(comment.name))

if __name__ == '__main__':
    main()