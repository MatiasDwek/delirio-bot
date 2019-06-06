import os

class Config:
    """ Holds the bot's configuration """
    SUBREDDITS = ['pythonforengineers', 'testabot'] # ['Argentinacirclejerk', 'argentina', 'republicaargentina']
    REPLY_WAIT_TIME = 120.0 # 2 minutes, in seconds
    USER_WAIT_TIME = 43200.0 # 12 hours, in seconds
    IGNORED_TAGS = ['serio', 'serious', 'enserio']
    BOT_NAME = 'DelirioBot'
    TRIGGER_WORD = '!delirio'
    BOT_RELOAD_TIME = 600.0 # 10 minutes

    DATABASE_PATH = os.environ['DELIRIO_DATABASE_PATH']
    LOGGING_PATH = os.environ['DELIRIO_LOGGING_PATH']
    CLIENT_ID = os.environ['DELIRIO_CLIENT_ID']
    CLIENT_SECRET = os.environ['DELIRIO_CLIENT_SECRET']
    PASSWORD = os.environ['DELIRIO_PASSWORD']
    USERNAME = os.environ['DELIRIO_USERNAME']
    USER_AGENT = os.environ['DELIRIO_USER_AGENT']