#!/usr/bin/python

import praw
import re
import random
import time

from deliriobot.comments_db_utils import *

class DelirioBot:

    def __init__(self):
        self.properties = dict()
        self.properties['answer_wait'] = 120.0  # 2 minutes (in seconds)
        self.properties['user_wait'] = 43200.0  # 12 hours (in seconds)

        self.wait_time = self.properties['answer_wait'] # (in seconds)

        # self.subreddits = ['Argentinacirclejerk', 'argentina', 'republicaargentina']
        self.subreddits = ['pythonforengineers']

        self.con = db_connect()
        self.cur = self.con.cursor()

    def random_line(self, file_name):
        file = open(file_name, mode="r", encoding="utf-8")
        line = next(file)
        for num, aline in enumerate(file, 2):
          if random.randrange(num): continue
          line = aline
        return line

    def generate_reply(self):
        con_img = db_connect(os.path.join(os.path.dirname(__file__), 'images.sqlite3'))
        cur_img = con_img.cursor()
        cur_img.execute('SELECT * FROM images ORDER BY RANDOM() LIMIT 1') # Select random image from image database
        reply = "[{0}](https://i.imgur.com/{1})\n\n" \
                "&nbsp;\n" \
                "- - - - - -\n" \
                "^*DelirioBot* ^- " \
                "[^Source ^code](https://github.com/MatiasDwek/delirio-bot/tree/master/deliriobot)" \
                .format(self.random_line("../delirio-bot-data/replies.txt"), cur_img.fetchone()[0])

        return reply

    def reply(self, comment):
        if validate_request(comment):
            self.cur.execute("SELECT MAX(date) FROM comments WHERE should_reply = 'FALSE'")
            last_comment_date = self.cur.fetchone()[0]
            if last_comment_date is None:
                last_comment_date = 0
            delta_time = comment.created_utc - last_comment_date
            # Before posting a reply, ask if the bot is posting replies too often
            if delta_time > self.wait_time:
                # Post reply
                try:
                    print('Here goes the reply to comment {}'.format(comment.body))
                    comment.reply(self.generate_reply())
                    self.cur.execute('UPDATE comments SET should_reply = \'FALSE\' WHERE id=?', [comment.name])
                    self.con.commit()

                    # Reset the default reply wait time
                    self.wait_time = self.properties['answer_wait']
                except praw.exceptions.APIException as e:
                    if e.error_type == 'RATELIMIT':
                        string_minutes = re.search(r'try again in (.*) minutes', e.message)
                        if string_minutes is None:
                            self.wait_time = 10 * 60 # wait for 10 minutes
                        else:
                            self.wait_time = (int(string_minutes.group(1)) + 1) * 60
                        print('bot is rate limited, waiting {} seconds'.format(self.wait_time))
        else:
            self.cur.execute('UPDATE comments SET should_reply = \'IGNORE\' WHERE id=?', [comment.name])
            self.con.commit()

    def loop(self):
        reddit = praw.Reddit('delirio-bot')
        all_subreddits = reddit.subreddit('+'.join(self.subreddits))

        for comment in all_subreddits.stream.comments():
            # TODO sleep for a couple of seconds
            # time.sleep(5)
            if re.match("!delirio", comment.body, re.IGNORECASE):
                self.cur.execute("SELECT count(*) FROM comments WHERE id = ?", (comment.name,))
                if self.cur.fetchone()[0] == 0:
                    save_request(comment, reddit)

                self.cur.execute('SELECT should_reply FROM comments WHERE id = ?', (comment.name,))
                if self.cur.fetchone()[0] == 'TRUE':
                    self.reply(comment)
                else:
                    print('The request from {} does not need a reply'.format(comment.name))

if __name__ == '__main__':
    delirio_bot = DelirioBot()
    delirio_bot.loop()