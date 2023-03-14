# coding-memes-bot

A Twitter bot ([@CodingMemesBot](https://twitter.com/CodingMemesBot)) that reposts the funniest coding memes from Reddit.
The bot currently posts a meme every hour. 

It uses the following AWS services:
- *AWS Lambda* for running the code that fetches the posts and also the code that tweets them
- *AWS RDS* (Postgres instance) for storing the fetches funniest Reddit posts
- *AWS EventBridge* for scheduling the 2 Lambda functions
- *AWS CloudWatch* for logging
