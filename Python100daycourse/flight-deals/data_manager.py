import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from pprint import pprint
# Load environment variables from .env file
load_dotenv()

URL_SHEETY_ENDPOINT = "https://api.sheety.co/ff480bd3db2fae69ac2f8bf260c9221b/flightDeals/prices"

class DataManager:
    #This class is responsible for talking to the Google Sheet.
    def __init__(self):
        self._user = os.environ["SHEETY_USERNAME"]
        self._password = os.environ["SHEETY_PASSWORD"]
        self._authorization = HTTPBasicAuth(self._user, self._password)
        self.destination_data = {}

    def get_destination_data(self):
        response = requests.get(url=URL_SHEETY_ENDPOINT, auth=self._authorization)
        data = response.json()
        self.destination_data = data["prices"]
        #pprint(data)
        return self.destination_data

    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": { "iataCode": city["iataCode"] }
            }
            response = requests.put(
                url=f"{URL_SHEETY_ENDPOINT}/{city['id']}",
                json=new_data,
                auth=self._authorization)
            result = response.json()
            print(result)

