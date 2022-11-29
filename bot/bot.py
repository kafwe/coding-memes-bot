import requests
import tweepy
from PIL import Image
from io import BytesIO
import os
import logging
import psycopg2
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Connect to Postgres
try:
    connection = psycopg2.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        database=os.environ["DB_NAME"],
    )
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to Postgres instance.")
    logger.error(e)
    sys.exit()

# Connect to Twitter
auth = tweepy.OAuthHandler(
    os.environ["TWITTER_CONSUMER_KEY"], os.environ["TWITTER_CONSUMER_SECRET"]
)
auth.set_access_token(
    os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
)

api = tweepy.API(auth)


def create_tweet(post):
    """Creates a tweet from a reddit post"""

    tweet = {
        "id": post[0],
        "text": post[1],
        "author": post[2],
        "subreddit": post[3],
        "reddit_post_url": post[4],
        "image_url": post[5],
    }

    return tweet


def tweet_meme(tweet):
    """Tweets a meme"""

    response = requests.get(tweet["image_url"])
    image = Image.open(BytesIO(response.content))
    filename = tweet["image_url"].split("/")[-1]
    image.save(f"tmp/{filename}")
    media = api.media_upload(filename=f"tmp/{filename}")
    api.update_status(status=tweet["title"], media_ids=[media.media_id])


def tweet_meme_info(tweet):
    """Tweets meme info. This is a reply to the meme tweet
    containing the author and subreddit"""

    last_tweet = api.user_timeline(count=1)[0]

    api.update_status(
        f'Posted by {tweet["author"]} in {tweet["subreddit"]}\
        \n\n{tweet["reddit_post_url"]}',
        in_reply_to_status_id=last_tweet.id,
    )
