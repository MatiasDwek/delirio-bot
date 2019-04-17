import praw
import re
import random
from deliriobot.db_utils import *
from deliriobot.validate import *

def validate_request(comment_id):
    return True