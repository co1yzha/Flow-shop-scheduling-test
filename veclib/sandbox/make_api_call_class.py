import requests
import json

# -- 1. make api call
class MakeApiCall():

    # --- 1. 1 get_data
    def get_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            print("sucessfully fetched the data")
            self.response = response.json()
        else:
            print(f"There is a {response.status_code} error with your request")

    # --- 1. 2 get_user_data
    def get_paras_data(self):
        response = requests.get(self.url, params=self.paras)
        if response.status_code == 200:
            print("sucessfully fetched the data with parameters")
            self.response = response.json()
        else:
            print(f"There is a {response.status} error with your request.")

    # --- 1. 3 get_user_data
    def get_header_data(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            print("sucessfully fetched the data with parameters")
            self.response = response.json()
        else:
            print(f"There is a {response.status} error with your request.")
            
    def get_paras_header_data(self):
        response = requests.get(self.url, params=self.params, headers=self.headers)
        if response.status_code == 200:
            print("sucessfully fetched the data with parameters and hearders")
            self.response = response.json()
        else:
            print(f"There is a {response.status} error with your request")

    # --- 1. 3 formatted_print
    # def formatted_print(self, obj):
    #     return json.dump(obj, sort_keys=True, indent=4)

    # --- 1. 4 __init__()
    def __init__(self, url, parameters = {}, headers = {}):
        self.url = url
        self.response = {}
        if parameters.__len__() == 0 & headers.__len__() == 0:
            self.get_data()
        elif parameters.__len__() > 0 & headers.__len__() == 0:
            self.params = parameters
            self.get_paras_data()
        elif parameters.__len__() == 0 & headers.__len__() > 0:
            self.headers = headers
            self.get_header_data()
        else:
            self.params = parameters
            self.headers = headers
            self.get_paras_hearder_data()





