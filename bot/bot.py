"""Lambda function that tweets memes from the database.
"""

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


def lambda_handler(event, context):
    post = get_post()

    if post:
        tweet = create_tweet(post)
        tweet_meme(tweet)
        tweet_meme_info(tweet)
        update_post(tweet)
        logger.info(f"Tweeted post {tweet['id']}")
    else:
        logger.info("No new posts to tweet")


def create_tweet(post):
    """Convert a reddit post tuple into a tweet dictionary."""

    tweet = {
        "id": post[0],
        # skip created_at field
        "text": post[2],
        "author": post[3],
        "subreddit": post[4],
        "reddit_post_url": post[5],
        "image_url": post[6],
    }

    return tweet


def tweet_meme(tweet):
    """Tweets a meme"""

    response = requests.get(tweet["image_url"])
    image = Image.open(BytesIO(response.content))
    filename = tweet["image_url"].split("/")[-1]
    image.save(f"/tmp/{filename}")
    media = api.media_upload(filename=f"/tmp/{filename}")
    api.update_status(status=tweet["text"], media_ids=[media.media_id])


def tweet_meme_info(tweet):
    """Tweets meme info. This is a reply to the meme tweet
    containing the author and subreddit"""

    last_tweet = api.user_timeline(count=1)[0]

    api.update_status(
        f'Posted by {tweet["author"]} in {tweet["subreddit"]}\
        \n\n{tweet["reddit_post_url"]}',
        in_reply_to_status_id=last_tweet.id,
    )


def get_post():
    """Gets the most recent untweeted post from the database."""

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM posts WHERE tweeted=false ORDER BY created_at ASC LIMIT 1"
        )
        post = cursor.fetchone()

    return post


def update_post(post):
    """Updates the post in the database to tweeted=true"""

    with connection.cursor() as cursor:
        cursor.execute("UPDATE posts SET tweeted=true WHERE post_id=%s", (post["id"],))
        connection.commit()
