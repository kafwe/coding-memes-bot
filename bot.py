import requests

response = requests.get(
    "https://www.reddit.com/r/ProgrammerHumor/top.json",
    headers={"user-agent": "scraping posts for @CodingMemesBot twitter bot"},
).json()
reddit_posts = response["data"]["children"]


def create_tweet(post):
    """Creates a tweet from a reddit post"""

    tweet = {
        "title": post["data"]["title"],
        "author": f'u/{post["data"]["author"]}',
        "post_url": f'www.reddit.com/{post["data"]["permalink"]}',
        "image_url": post["data"]["url"],
    }

    return tweet


def is_valid(post):
    """Checks if a reddit post is valid for a tweet.
    That is the post type is Meme and it has an image."""

    is_text = post["data"]["is_self"]

    if is_text:
        return False

    is_image = post["data"]["url"].endswith((".jpg", ".png"))
    is_meme = post["data"]["link_flair_text"] == "Meme"

    return is_meme and is_image
