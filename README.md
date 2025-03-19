# Paper Ninja Bot
[![Watch the video](https://img.youtube.com/vi/cu1IVtf96NQ/0.jpg)](https://www.youtube.com/watch?v=cu1IVtf96NQ)

**Paper Ninja Bot** is a Telegram bot developed for the National Learn AI Challenge. It leverages the [SGNLP](https://github.com/SGNLP) Python package to assist users in conducting secondary research. The bot uses aspect-based sentiment analysis to classify the sentiment (positive or negative) of five retrieved links based on a keyword provided by the user.

## Features

- **Telegram Integration:** Interact with the bot directly on Telegram.
- **Aspect-Based Sentiment Analysis:** Classify sentiment of research links.
- **Automated Search:** Retrieve and analyze five research links based on user-provided keywords.

## Required Python Packages

Install the following packages using `pip`:

```bash
pip install googlesearch-python
pip install python-telegram-bot
pip install requests
pip install beautifulsoup4
