import time
import requests
import json


# --- 1. 1 get_data
def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Successfully fetched the data")
    else:
        print(f"ERROR: {response.content}")
    return response.json()

# --- 1. 2 get_user_data
def get_paras_data(url, paras):
    response = requests.get(url, params=paras)
    if response.status_code == 200:
        print("Successfully fetched the data with parameters")
    else:
        print(f"ERROR: {response.content}")
    return response.json()

# --- 1. 3 get_user_data
def get_header_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Successfully fetched the data with parameters")
    else:
        print(f"ERROR: {response.content}")
    return response.json()

def get_paras_header_data(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        print("Successfully fetched the data with parameters and hearders")
    else:
        print(f"ERROR: {response.content}")
    return response.json()


def post_header_data(url, headers, data):
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Successfully post the data with headers")
    else:
        print(f"ERROR: {response.content}")
    return response.json()

# --- 1. 3 formatted_print
# def formatted_print(self, obj):
#     return json.dump(obj, sort_keys=True, indent=4)

# -- retry logic:
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests


