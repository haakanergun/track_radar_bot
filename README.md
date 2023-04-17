# TrackRadar

TrackRadar is a Twitter bot that identifies and provides information about songs in tweeted videos. The bot can be triggered by mentioning the bot's username in a tweet, or by tweeting a video and asking for the song's name in a reply. TrackRadar will analyze the video and reply with the artist's name, song title, and a link to the song on YouTube.

## Features

- Recognizes songs in videos tweeted by users
- Supports multiple languages for search queries
- Replies with song information, including:
    - Artist name
    - Song title
    - YouTube URL for the song

## Installation and Setup

1. Clone the repository:

```
git clone https://github.com/haakanergun/track_radar_bot.git
```

2. Navigate to the project directory:

```
cd track_radar_bot
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Run the bot:
```
python bot_v3.py
```


## How to Use

1. Mention the bot's username in a tweet containing a video, or ask for the song's name in a reply to a tweet containing a video.
2. The bot will analyze the video, identify the song, and reply with the song information.

## Supported Languages

TrackRadar currently supports the following languages for search queries:

- English
- Turkish

## Dependencies

- tweepy
- acrcloud
- google-api-python-client


## Contributing

Contributions are welcome! If you have any suggestions, ideas, or improvements, please feel free to create a pull request or open an issue.



