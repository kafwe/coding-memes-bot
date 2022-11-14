import requests

response = requests.get(
    "https://www.reddit.com/r/ProgrammerHumor/top.json",
    headers={"user-agent": "scraping posts for @CodingMemesBot twitter bot"},
).json()
reddit_posts = response["data"]["children"]
