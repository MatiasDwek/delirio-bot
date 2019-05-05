#!/usr/bin/python

import praw
import re
import random
import time
import argparse

from deliriobot.delirio_db_utils import *

class DelirioBot:

    def __init__(self, subreddits, default_wait = 120.0):
        self.default_wait = default_wait
        self.subreddits = subreddits
        self.wait_time = self.default_wait

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
        reply = "[{0}](https://i.imgur.com/{1})\n\n" \
                "&nbsp;\n" \
                "- - - - - -\n" \
                "^*DelirioBot* ^- " \
                "[^Source ^code](https://github.com/MatiasDwek/delirio-bot/tree/master/deliriobot)" \
                .format(self.random_line("deliriobot/resources/replies.txt"), self.random_line('deliriobot/resources/imgur_links.txt'))

        return reply

    def reply(self, comment):
        if validate_request(comment):
            while 1:
                # Post reply
                try:
                    print('Here goes the reply to comment {}'.format(comment.body))
                    comment.reply(self.generate_reply())
                    # print(self.generate_reply())
                    self.cur.execute('UPDATE comments SET should_reply = \'FALSE\' WHERE id=?', [comment.name])
                    self.con.commit()

                    # Reset the default reply wait time
                    self.wait_time = self.default_wait
                    break
                except praw.exceptions.APIException as e:
                    if e.error_type == 'RATELIMIT':
                        string_minutes = re.search(r'try again in (.*) minutes', e.message)
                        if string_minutes is None:
                            self.wait_time = 10 * 60 # wait for 10 minutes
                        else:
                            self.wait_time = (int(string_minutes.group(1)) + 1) * 60
                        print('bot is rate limited, waiting {} seconds'.format(self.wait_time))
                        time.sleep(self.wait_time)
        else:
            self.cur.execute('UPDATE comments SET should_reply = \'IGNORE\' WHERE id=?', [comment.name])
            self.con.commit()

    def loop(self):
        reddit = praw.Reddit('delirio-bot')
        selected_subreddits = reddit.subreddit('+'.join(self.subreddits))
        for comment in selected_subreddits.stream.comments():
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
    # ['Argentinacirclejerk', 'argentina', 'republicaargentina']
    delirio_bot = DelirioBot(['pythonforengineers'])
    delirio_bot.loop()