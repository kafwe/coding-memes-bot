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
