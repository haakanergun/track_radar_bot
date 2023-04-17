import tweepy
import requests
import json
import acrcloud
from acrcloud.recognizer import ACRCloudRecognizer
from tweepy import Client
import time
import random
import tweepy.errors

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



API_KEY_GOOGLE = "YOUR_GOOGLE_API_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY_GOOGLE)



YASAKLI_KELIMELER = [

    #The bot will censor profane words that are contained in the song to avoid being blocked by Twitter. The list of profane words should be added to the code.

   "kelime1",'kelime2','kelime3'
]


not_find_messages = [  #The bot will write messages with content that indicate it couldn't find the requested music in the response.
    
    'message1','message2']            

search_messages = [

    #You can write messages with content that include tagging me in the response of the bot for next time.
 
    'message1','message2'
        
    ]

#Twitter Api
def create_api():
    access_token = "YOUR_ACCESS_TOKEN"
    access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret="YOUR_CONSUMER_SECRET"


    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    return api


# ACRCloud credentials

def create_recognizer():
    acrcloud_config = {
        'host': 'identify-eu-west-1.acrcloud.com',
        'access_key': 'YOUR_ACCESS_KEY',
        'access_secret': 'YOUR_ACCESS_SECRET',
        'timeout': 10
    }

    recognizer = ACRCloudRecognizer(acrcloud_config)
    return recognizer

def get_video_data(api, tweet_id):
    tweet = api.get_status(tweet_id, tweet_mode='extended')
    
    if not hasattr(tweet, 'extended_entities'):
        return None

    if 'media' not in tweet.extended_entities:
        return None
    try:
        video_url = tweet.extended_entities['media'][0]['video_info']['variants'][0]['url']
        response = requests.get(video_url)
        video_data = response.content

        
    except:
        return None
    return video_data

def format_time(milliseconds):
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    return "{}:{:02d}".format(minutes, seconds)
import re

def sansurle(metin):
    sansürsüz_metin = metin
    for kelime in YASAKLI_KELIMELER:
        sansürsüz_metin = re.sub(f"\\b{kelime}\\b", "****", sansürsüz_metin, flags=re.IGNORECASE)
    return sansürsüz_metin

def find_similar_songs(artist, song):
    # arama sorgusunu oluşturun
    query = artist + " " + song

    # youtube api ile arama yapın
    response = youtube.search().list(
    part="snippet",
    q=query,
    type="video",
    maxResults=1
    ).execute()

    # arama sonuçlarını bir liste olarak alın
    result = response["items"]

    # sonuçlardan video id ve başlıklarını alın

    video_id = result[0]["id"]["videoId"]

        
    return video_id

def reply_with_music_details_for_search(api, tweet_id, recognizer, video_data,messages=search_messages):
    try:
        
        result = recognizer.recognize_by_filebuffer(video_data, 0)
        data = json.loads(result)
        music_list = data["metadata"]["music"]

        random_message = random.choice(messages)

        music = music_list[0]
        reply_text = ""
        artist = music["artists"][0]["name"]
        title = music["title"]


        try:
            youtube_id = find_similar_songs(artist,title)
        except:

            try:
                youtube_id = music['external_metadata']['youtube']['vid']
            except:
                youtube_id = ""

        reply_text += "{}\n".format(random_message)

        reply_text += "\n"

        reply_text += "{} ".format(title)

        reply_text += "by {}\n".format(artist)

        reply_text += "\n"

        if youtube_id !="":
            reply_text += "Link: https://www.youtube.com/watch?v={}\n".format(youtube_id)


        api.update_status(status=sansurle(reply_text), in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)


    except KeyError as e:
        
        pass

def reply_with_music_details_for_mentions(api, tweet_id, recognizer, video_data,messages=not_find_messages):
    try:
        result = recognizer.recognize_by_filebuffer(video_data, 0)
        data = json.loads(result)
        music_list = data["metadata"]["music"]



        music = music_list[0]
        reply_text = ""
        artist = music["artists"][0]["name"]
        title = music["title"]

        try:
            youtube_id = find_similar_songs(artist,title)
        except:

            try:
                youtube_id = music['external_metadata']['youtube']['vid']
            except:
                youtube_id = ""

        reply_text += "{} ".format(title)

        reply_text += "by {}\n".format(artist)

        reply_text += "\n"

        if youtube_id !="":
            reply_text += "Link: https://www.youtube.com/watch?v={}\n".format(youtube_id)


        api.update_status(status=sansurle(reply_text), in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)


    except KeyError as e:
        random_message = random.choice(messages)


        
        reply_text = ""
        reply_text += "{}\n".format(random_message)


        api.update_status(status=reply_text, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)

def check_mentions(api, since_id,recognizer):
    
    new_since_id = since_id
    for tweet in api.mentions_timeline(since_id=since_id):
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            try:
                mentioned_tweet = api.get_status(tweet.in_reply_to_status_id)
            except:
                continue
            if mentioned_tweet.id is not None:
                video_data = get_video_data(api, mentioned_tweet.id)
                if video_data is not None:
                    reply_with_music_details_for_mentions(api, tweet.id, recognizer, video_data)
                    time.sleep(5)
    
    return new_since_id

def search_tweets(api, recognizer, query, since_id=None):
    search_results = api.search_tweets(q=query, since_id=since_id,count=100,result_type='recent', tweet_mode='extended')

    new_since_id = since_id
    for result in search_results:
        if not result.retweeted and 'RT @' not in result.full_text:
            new_since_id = max(result.id, new_since_id)
            if result.in_reply_to_status_id is not None:
                try:
                    mentioned_tweet = api.get_status(result.in_reply_to_status_id)
                except:
                    continue
                
                if mentioned_tweet.id is not None:
                    
                    video_data = get_video_data(api, mentioned_tweet.id)
                    if video_data is not None:
                        
                        reply_with_music_details_for_search(api, result.id, recognizer, video_data)
                        time.sleep(5)
    return new_since_id




def get_latest_tweet_id(api):
    tweets = api.search_tweets(q="şarkı", lang="tr", count=1)
    if len(tweets) > 0:
        return tweets[0].id
    return 1

def get_latest_mention_id(api):
    mentions = api.mentions_timeline(count=1)
    if len(mentions) > 0:
        return mentions[0].id
    return 1

def main():
    api = create_api()
    recognizer = create_recognizer()

    reply_patterns = [
    # Türkçe
    "şarkı ismi", "şarkı adı", "şarkının ismi", "şarkının adı",
    
    # İngilizce
    "song name",

]

    since_id_mentions = get_latest_mention_id(api)
    since_id_search_dict = {}
    for pattern in reply_patterns:
        since_id_search_dict[pattern] = get_latest_mention_id(api)


  


    while True:
        since_id_mentions = check_mentions(api, since_id_mentions, recognizer)

        for pattern in reply_patterns:
            time.sleep(2)
            since_id_search_dict[pattern] = search_tweets(api, recognizer,  pattern , since_id=since_id_search_dict[pattern])

        time.sleep(60)



if __name__ == "__main__":
    main()
