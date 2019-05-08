class Config:
    """ Holds all the configurations for the bot """
    SUBREDDITS = ['pythonforengineers', 'testabot'] # ['Argentinacirclejerk', 'argentina', 'republicaargentina']
    REPLY_WAIT_TIME = 120.0 # 2 minutes, in seconds
    USER_WAIT_TIME = 43200.0 # 12 hours, in seconds
    IGNORED_TAGS = ['serio', 'serious', 'enserio']
    BOT_NAME = 'DelirioBot'
    TRIGGER_WORD = '!delirio'
    LOGGING_PATH = 'delirio.log'
    DATABASE_PATH = 'delirio.sqlite3'