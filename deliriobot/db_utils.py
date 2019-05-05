import os
import sqlite3

from deliriobot.config import *

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), DELIRIO_CONFIG['db_path'])

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con