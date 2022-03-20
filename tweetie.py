import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


MAX_FRIENDS = 100
MAX_TWEETS = 100

def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    # load credentials
    credentials = loadkeys(twitter_auth_filename)
    consumer_key = credentials[0]
    consumer_secret = credentials[1]
    access_token = credentials[2]
    access_token_secret = credentials[3]

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    tweets = list()
    sid_obj = SentimentIntensityAnalyzer()
    for status in tweepy.Cursor(api.user_timeline,screen_name=name).items(MAX_TWEETS):
        id = status.id
        created = status.created_at
        retweeted = status.retweet_count
        text = status.text
        score = sid_obj.polarity_scores(text)['compound']
        hashtags = []
        urls = []
        mentions = []
        if hasattr(status, "entities"):
            for key in status.entities:
                if key == 'hashtags' and status.entities['hashtags'] is not None:
                    for tag in status.entities['hashtags']:
                        hashtags.append(tag['text'])
                elif key == 'urls' and status.entities['urls'] is not None:
                    for url in status.entities['urls']:
                        urls.append(url['url'])
                elif key == 'user_mentions' and status.entities['user_mentions'] is not None:
                    for user in status.entities['user_mentions']:
                        mentions.append(user['screen_name'])
        tweets.append({'id': id, 'created': created, 'retweeted': retweeted, 'text': text, 'hashtags': hashtags, 'urls': urls, 'mentions': mentions, 'score': score})

    return {'user': name, 'count':len(tweets), 'tweets': tweets}



def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get the list of User objects back from friends();
    get a maximum of 100 results. Pull the appropriate values from
    the User objects and put them into a dictionary for each friend.
    """
    friends = list()
    for friend in tweepy.Cursor(api.get_friends, screen_name = name).items(MAX_FRIENDS):
        friends.append({'name': friend.name, 'screen_name': friend.screen_name, 'followers': friend.followers_count, 'created': str(friend.created_at.date()), 'image': friend.profile_image_url})
    return friends
    
