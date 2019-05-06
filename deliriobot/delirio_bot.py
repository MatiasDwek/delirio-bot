#!/usr/bin/python

import praw
import re
import random
import time
import logging

from deliriobot.delirio_db_utils import *
from deliriobot.config import *

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
                "[^Source ^code ](https://github.com/MatiasDwek/delirio-bot/tree/master)" \
                .format(self.random_line("deliriobot/resources/replies.txt"), self.random_line('deliriobot/resources/imgur_links.txt'))

        return reply

    def reply(self, comment):
        if validate_request(comment):
            while 1:
                # Post reply
                try:
                    comment.reply(self.generate_reply())
                    logging.info('Replied to comment from {0} with body \'{1}\''.format(comment.author.name, comment.body))
                    self.cur.execute('UPDATE comments SET should_reply = \'FALSE\' WHERE id=?', [comment.name])
                    self.con.commit()

                    # Reset the default reply wait time
                    self.wait_time = self.default_wait
                    break
                except praw.exceptions.APIException as e:
                    if e.error_type == 'RATELIMIT':
                        string_minutes = re.search(r'try again in (.*) minute', e.message)
                        if string_minutes is None:
                            self.wait_time = 10 * 60 # wait for 10 minutes
                        else:
                            self.wait_time = (int(string_minutes.group(1)) + 1) * 60
                        logging.warning('Bot is rate limited, waiting {0} seconds to reply. Reddit message was \'{1}\''.format(self.wait_time, e.message))
                        time.sleep(self.wait_time)
                    elif e.error_type == 'DELETED_COMMENT':
                        logging.info('Comment {} was deleted, skipping reply'.format(comment.name))
        else:
            self.cur.execute('UPDATE comments SET should_reply = \'IGNORE\' WHERE id=?', [comment.name])
            self.con.commit()
            logging.info('Received an invalid request')


    def loop(self):
        reddit = praw.Reddit('delirio-bot')
        selected_subreddits = reddit.subreddit('+'.join(self.subreddits))
        for comment in selected_subreddits.stream.comments():
            if re.match(DELIRIO_CONFIG['keyword'], comment.body, re.IGNORECASE):
                self.cur.execute("SELECT count(*) FROM comments WHERE id = ?", (comment.name,))
                if self.cur.fetchone()[0] == 0:
                    save_request(comment, reddit)

                self.cur.execute('SELECT should_reply FROM comments WHERE id = ?', (comment.name,))
                if self.cur.fetchone()[0] == 'TRUE':
                    self.reply(comment)
                else:
                    logging.info('The request {0} from  {1} does not need a reply'.format(comment.name, comment.author.name))

if __name__ == '__main__':
    logging.basicConfig(filename=DELIRIO_CONFIG['logging_path'],
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    logging.info('Starting bot...')
    delirio_bot = DelirioBot(DELIRIO_CONFIG['subreddits'], DELIRIO_CONFIG['reply_wait_time'])
    delirio_bot.loop()