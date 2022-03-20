"""
A server that responds with two pages, one showing the most recent
100 tweets for given user and the other showing the people that follow
that given user (sorted by the number of followers those users have).

For authentication purposes, the server takes a commandline argument
that indicates the file containing Twitter data in a CSV file format:
[consumer_key, consumer_secret, access_token, access_token_secret]
"""
import sys
from flask import Flask, render_template
from tweetie import *
from colour import Color

from numpy import median

app = Flask(__name__)

MAX_TWEETS = 100

def score_conversion(input, score_start = -1, score_end = 1, index_start = 0, index_end = 100):
    # method reference to 
    # https://math.stackexchange.com/questions/377169/going-from-a-value-inside-1-1-to-a-value-in-another-range
    return round((input - score_start)*((index_end - index_start)/(score_end - score_start))+index_start)

def add_color(tweets):
    """
    Given a list of tweets, one dictionary per tweet, add
    a "color" key to each tweets dictionary with a value
    containing a color graded from red to green. Pure red
    would be for -1.0 sentiment score and pure green would be for
    sentiment score 1.0.
    """
    colors = list(Color("red").range_to(Color("green"), 100))
    for t in tweets:
        score = t['score']
        color_index = score_conversion(score)
        t['color'] = colors[color_index]


@app.route("/favicon.ico")
def favicon():
    """
    Open and return a 16x16 or 32x32 .png or other image file in binary mode.
    This is the icon shown in the browser tab next to the title.
    """
    with open('./favicon.gif', 'rb') as f:
        return f.read()


@app.route("/<name>")
def tweets(name):
    "Display the tweets for a screen name color-coded by sentiment score"
    tweets_dict = fetch_tweets(api, name)
    user_name = tweets_dict['user']
    score_median = median([tweet['score'] for tweet in tweets_dict['tweets']])
    add_color(tweets_dict['tweets'])
    return render_template('tweets.html', user_name = user_name, score_median = score_median, tweets = tweets_dict['tweets'])


@app.route("/following/<name>")
def following(name):
    """
    Display the list of users followed by a screen name, sorted in
    reverse order by the number of followers of those users.
    """
    friends = fetch_following(api, name)
    sorted_friends = sorted(friends, key=lambda user: user['followers'], reverse=True)
    return render_template('following.html', name = name, friends = sorted_friends)


i = sys.argv.index('server:app')
twitter_auth_filename = sys.argv[i+1]
api = authenticate(twitter_auth_filename)

# if __name__ == '__main__':
#     twitter_auth_filename = './twitter.csv'
#     api = authenticate(twitter_auth_filename)
#     app.run(host='0.0.0.0', port=80)

