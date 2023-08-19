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

# Twitter V1 API client for uploading images
auth = tweepy.OAuthHandler(
    os.environ["TWITTER_CONSUMER_KEY"], os.environ["TWITTER_CONSUMER_SECRET"]
)

auth.set_access_token(
    os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
)

api = tweepy.API(auth)

# Twitter API V2 client for creating tweets
client = tweepy.Client(
    consumer_key=os.environ["TWITTER_CONSUMER_KEY"], 
    consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
    access_token=os.environ["TWITTER_ACCESS_TOKEN"], 
    access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
)


def lambda_handler(event, context):
    post = get_post()

    if post:
        tweet = create_tweet(post)
        tweet_id = tweet_meme(tweet)
        tweet_meme_info(tweet, tweet_id)
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
    """Tweets a meme and returns the tweet id."""

    response = requests.get(tweet["image_url"])
    image = Image.open(BytesIO(response.content))
    filename = tweet["image_url"].split("/")[-1]
    image.save(f"/tmp/{filename}")
    media = api.media_upload(filename=f"/tmp/{filename}")
    tweet_response = client.create_tweet(text=tweet["text"], media_ids=[media.media_id])
    return tweet_response.data["id"]


def tweet_meme_info(tweet, last_tweet_id):
    """Tweets meme info. This is a reply to the meme tweet
    containing the author and subreddit"""

    client.create_tweet(
        text=f'Posted by {tweet["author"]} in {tweet["subreddit"]}\
        \n\n{tweet["reddit_post_url"]}',
        in_reply_to_tweet_id=last_tweet_id,
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