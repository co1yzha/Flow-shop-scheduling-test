import pandas as pd
import numpy as np
import json
import nltk
import warnings
import datetime
import requests


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def create_url(keyword, start_date, end_date, max_results=10):
    search_url = "https://api.twitter.com/2/tweets/search/recent"  # Change to the endpoint you want to collect data from
    count_url = "https://api.twitter.com/2/tweets/counts/recent"
    # change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    query_count_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date}

    return (search_url, query_params, count_url, query_count_params)


def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


warnings.filterwarnings("ignore")
with open("../data/keys.json") as f:
    keys = json.load(f)

headers = create_headers(keys['twitter']['bearer_token'])
key_words = 'supply-chain'
search_query = f'({key_words}) lang:en -is:retweet'
start_time = datetime.datetime(2022,7,17).astimezone().isoformat()
end_time = datetime.datetime(2022,7,18).astimezone().isoformat()
max_results = 10

url = create_url(search_query, start_time,end_time, max_results)
json_response = connect_to_endpoint(url[0], headers, url[1])
total_count = connect_to_endpoint(url[2], headers, url[3])

