"""Lambda function that fetches posts from Reddit and 
inserts the valid meme posts from them into the database.
"""

import logging
import psycopg2
import os
import sys
import praw

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
except psycopg2.errors.OperationalError as e:
    logger.error("ERROR: Unexpected error: Could not connect to Postgres instance.")
    logger.error(e)
    sys.exit()

# Reddit API client
try:
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent="scraping posts for @CodingMemesBot twitter bot",
        refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
    )
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to Reddit instance.")
    logger.error(e)
    sys.exit()


def lambda_handler(event, context):
    try:
        reddit_posts = reddit.subreddit("ProgrammerHumor").top("day", limit=15)
    except Exception as e:
        logger.error("ERROR: Reddit API request unsuccessful")
        logger.error(e)
        sys.exit()

    for post in reddit_posts:
        if is_valid(post):
            # Prevent duplicate posts
            try:
                insert_post(post)
            except psycopg2.errors.UniqueViolation:
                connection.rollback()  # need to rollback because insert failed
                logger.info(f"Post {post.id} already exists in database")

def is_valid(post):
    """Checks if a reddit post is valid for a tweet.
    That is the post type is Meme and it has an image"""

    is_text = post.is_self

    if is_text:
        return False

    is_image = post.url.endswith((".jpg", ".png", ".jpeg"))
    is_meme = post.link_flair_text == "Meme"

    return is_meme and is_image

def insert_post(post):
    """Inserts a reddit post into the database"""

    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO posts (post_id, meme_text, author, subreddit, \
            reddit_post_url, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                post.id,
                post.title,
                post.author,
                f'r/{post.subreddit.display_name}',
                f'www.reddit.com{post.permalink}',
                post.url,
            ),
        )
        connection.commit()
