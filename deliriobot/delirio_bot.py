#!/usr/bin/python

import praw
import re
import random

from deliriobot.comments_db_utils import *

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
    reply = "[{0}](https://i.imgur.com/{1}.jpg)\n\n" \
            "&nbsp;\n" \
            "- - - - - -\n" \
            "^*DelirioBot* ^- " \
            "[^Source ^code](https://github.com/MatiasDwek/delirio-bot/tree/master/deliriobot)" \
            .format(random_line("../delirio-bot-data/replies.txt"), cur_img.fetchone()[0])

    return reply

def main():
    properties = dict()
    properties['answer_wait'] = 120.0  # 2 minutes
    properties['user_wait'] = 43200.0  # 12 hours

    reddit = praw.Reddit('delirio-bot')

    # subreddits = ['Argentinacirclejerk', 'argentina', 'republicaargentina']
    subreddits = ['pythonforengineers']
    all_subreddits = reddit.subreddit('+'.join(subreddits))

    con = db_connect()
    cur = con.cursor()

    for comment in all_subreddits.stream.comments():
        print(comment.body)
        if re.match("!delirio", comment.body, re.IGNORECASE):
            cur.execute("SELECT count(*) FROM comments WHERE id = ?", (comment.name,))
            if cur.fetchone()[0] == 0:
                save_request(comment, reddit)

            cur.execute('SELECT should_reply FROM comments WHERE id = ?', (comment.name,))
            if cur.fetchone()[0] == 'TRUE':
                if validate_request(comment):
                    cur.execute("SELECT MAX(date) FROM comments WHERE should_reply = 'FALSE'")
                    last_comment_date = cur.fetchone()[0]
                    if last_comment_date is None:
                        last_comment_date = 0
                    delta_time = comment.created_utc - last_comment_date
                    # Before posting a reply, ask if the bot is posting replies.txt too often
                    if delta_time > properties['answer_wait']:
                        # Post reply
                        comment.reply(generate_reply())
                        print('Here goes the reply to comment {}'.format(comment.body))
                        # After posting reply, save it in the db
                else:
                    cur.execute('UPDATE comments SET should_reply = \'IGNORE\' WHERE id=?', [comment.name])
                    con.commit()
            else:
                print('The request from {} does not need a reply'.format(comment.name))


if __name__ == '__main__':
    main()