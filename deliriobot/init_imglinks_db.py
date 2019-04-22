from imgurpython import ImgurClient
import sys

from deliriobot.db_utils import db_connect

client_id = sys.argv[1]
client_secret = sys.argv[2]

client = ImgurClient(client_id, client_secret)

# Path to the file with Imgur albums ids where the images with delirios can be found
# This allows the bot to retrieve delirios from multiple albums
fname = sys.argv[3]
with open(fname) as f:
    albums_ids = f.readlines()
albums_ids = [x.strip() for x in albums_ids]

con = db_connect('images.sqlite3')
cur = con.cursor()

# Table with Imgur images ids
# An image can be accessed by the URL imgur.com/{id}.jpg
images_sql = """
CREATE TABLE images (
  id text PRIMARY KEY)"""

cur.execute(images_sql)

for album_id in albums_ids:
    images = client.get_album_images(album_id)
    for image in images:
        query = 'SELECT EXISTS(SELECT 1 FROM images WHERE id=?) LIMIT 1'
        check = cur.execute(query, (image.id,))
        if check.fetchone()[0] == 0:
            image_sql = 'INSERT INTO images (id) VALUES (?)'
            cur.execute(image_sql, (image.id,))

con.commit()


