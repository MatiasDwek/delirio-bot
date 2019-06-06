# DelirioBot

Code for the [Reddit bot DelirioBot](https://old.reddit.com/user/deliriobot/).
DelirioBot is a bot that listens for requests and answers them by posting a message with an Imgur media link. Both the message and the Imgur link are chosen random from a list of options, stored in their corresponding text files.

The bot is written in [Python3](https://www.python.org/) and uses [PRAW](https://praw.readthedocs.io/en/latest) as the Reddit API Wrapper and [SQLite](https://www.sqlite.org/index.html) as the database manager that stores and queries the requests parsed.

## Setup

### Modules
To launch DelirioBot you need to install the modules mentioned above. You can do this by using the following [PIP](https://pypi.org/project/pip/) commands:

```sh
pip install praw
pip install sqlite3
```

### Configuration and environment variables

DelirioBot is configured through the file deliriobot/config.py:

| Variable        | Description |
| -------------   | ------------- |
| SUBREDDITS      | The subreddits the bot will listen to for requests |
| REPLY_WAIT_TIME | The default backoff wait time for the bot's replies |
| USER_WAIT_TIME  | How often a user is allowed to request the bot; if exceeded by a user, the bot ignores the request |
| BOT_NAME        | The bot's name in Reddit |
| TRIGGER_WORD    | Word to request the bot |
| BOT_RELOAD_TIME | Backoff time the bot takes to restart when it encounters an exception |

 and through environment variables:

| Environment variable        | Description |
| -------------   | ------------- |
| DELIRIO_DATABASE_PATH | Path where the database is located |
| DELIRIO_LOGGING_PATH  | Path where the logs will be stored |
| DELIRIO_CLIENT_ID     | Reddit API Client ID |
| DELIRIO_CLIENT_SECRET | Reddit API Client Secret |
| DELIRIO_PASSWORD      | Password of the bot's Reddit account |
| DELIRIO_USERNAME      | Username of the bot's Reddit account |
| DELIRIO_USER_AGENT    | Reddit API User Agent |


### Database

A database is needed to run DelirioBot. To configure it, you can launch the script deliriobot/init_database.py.

## Launching the bot

You can launch the bot by running the following command:

```sh
python3 deliriobot/delirio_bot.py
```

## Contributing

Pull requests and issues are always welcomed.

You can also contribute to either the Imgur media being used by the bot, located at: deliriobot/resources/imgur_links.txt, or to the replies being posted by it, at: deliriobot/resources/replies.txt. Note that the words in deliriobot/resources/imgur_links.txt correspond to the Imgur media ids, as described in [the Imgur official library](https://github.com/Imgur/imgurpython).

