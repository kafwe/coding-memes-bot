import requests
import html
import logging
import psycopg2
import os
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


def main():
    reddit_posts = get_posts("ProgrammerHumor")

    for reddit_post in reddit_posts:
        if is_valid(reddit_post):
            post = format_post(reddit_post)


def get_posts(subreddit):
    """Gets posts from Reddit API"""

    response = requests.get(
        f"https://www.reddit.com/r/{subreddit}/top.json?limit=15",
        headers={"user-agent": "scraping posts for @CodingMemesBot twitter bot"},
    )

    if response.status_code != 200:
        raise Exception("Reddit API request unsuccessful")

    response = response.json()
    reddit_posts = response["data"]["children"]
    return reddit_posts


def is_valid(post):
    """Checks if a reddit post is valid for a tweet.
    That is the post type is Meme and it has an image"""

    is_text = post["data"]["is_self"]

    if is_text:
        return False

    is_image = post["data"]["url"].endswith((".jpg", ".png"))
    is_meme = post["data"]["link_flair_text"] == "Meme"

    return is_meme and is_image


def format_post(post):
    """Formats a reddit post for a tweet"""

    post = {
        "id": post["data"]["id"],
        "text": html.unescape(post["data"]["title"]),
        "author": f'u/{post["data"]["author"]}',
        "subreddit": f'r/{post["data"]["subreddit"]}',
        "reddit_post_url": f'www.reddit.com/{post["data"]["permalink"]}',
        "image_url": post["data"]["url"],
    }

    return post
