"""
Python100daycourse/flight-deals/data_manager.py

# Purpose: This module defines DataManager, a class that reads/writes flight-price and customer data by talking to a Google Sheet through the Sheety API.

# Audience Note for Junior Programmers:
# Credentials (SHEETY_USERNAME, SHEETY_PASSWORD) and the two endpoint URLs (prices, users) are read from environment variables via os.environ, never hardcoded, so this module raises a KeyError at instantiation time if any is missing from the .env file.

# Dependencies (MUST be installed via pip): 
# - requests: HTTP calls to the Sheety API
# - python-dotenv: loads the .env file
"""
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from pprint import pprint
# Load environment variables from .env file
load_dotenv()

class DataManager:
    """This class wraps the Sheety API (a service exposing a Google Sheet as a REST API) to read flight-price rows and customer rows, and to update price rows with IATA airport codes. It holds two endpoint URLs (one for prices, one for users) and HTTP Basic Auth credentials built in __init__, plus two dict attributes (destination_data, customer_data) that start empty and get populated once the corresponding fetch method has been called."""
    #This class is responsible for talking to the Google Sheet.
    def __init__(self):
        """Reads the Sheety credentials and both endpoint URLs from environment variables, builds an HTTPBasicAuth object for use by the fetch/update methods, and initializes destination_data and customer_data as empty dicts (populated later by get_destination_data() and get_customer_emails() respectively). Fails fast with a KeyError naming the missing variable if any required environment variable is absent.

Parameters: None (reads SHEETY_USERNAME, SHEETY_PASSWORD, URL_SHEETY_ENDPOINT_PRICES, URL_SHEETY_ENDPOINT_USERS from the environment/.env file).
Returns: None."""
        self._user = os.environ["SHEETY_USERNAME"]
        self._password = os.environ["SHEETY_PASSWORD"]
        self._authorization = HTTPBasicAuth(self._user, self._password)
        self.prices_endpoint = os.environ["URL_SHEETY_ENDPOINT_PRICES"]
        self.users_endpoint = os.environ["URL_SHEETY_ENDPOINT_USERS"]
        self.destination_data = {}
        self.customer_data = {}

    def get_destination_data(self):
        """Fetches all rows from the Sheety "prices" endpoint via an authenticated GET request, stores the result in self.destination_data, and returns it. This is a side-effecting getter: it both updates the instance's stored destination_data and returns the same value, so callers can either use the return value directly or read self.destination_data afterward.

Parameters: None
Returns: list[dict] - the "prices" rows from the Sheety API response, one dict per destination row."""
        response = requests.get(url=self.prices_endpoint, auth=self._authorization)
        data = response.json()
        self.destination_data = data["prices"]
        #pprint(data)
        return self.destination_data

    def update_destination_codes(self):
        """Loops over self.destination_data (populated earlier by get_destination_data()) and, for each city row, sends a PUT request to that row's own Sheety endpoint URL (built from the row's "id") to overwrite its "iataCode" field with the value already present in that same row. This method must be called after get_destination_data() has populated self.destination_data - it does not fetch or return anything on its own, it only pushes an update back to the sheet.

Parameters: None (reads from self.destination_data, must be populated first).
Returns: None. Prints each PUT response's parsed JSON to stdout."""
        for city in self.destination_data:
            new_data = {
                "price": { "iataCode": city["iataCode"] }
            }
            response = requests.put(
                url=f"{self.prices_endpoint}/{city['id']}",
                json=new_data,
                auth=self._authorization)
            result = response.json()
            print(result)

    # Add a method called get_customer_emails() to your data_manager.py.
    # This should return the data on your "users" spreadsheet.
    def get_customer_emails(self):
        """Fetches all rows from the Sheety "users" endpoint via an authenticated GET request, stores the result in self.customer_data, and returns it - same side-effecting-getter pattern as get_destination_data().

Parameters: None.
Returns: list[dict] - the "users" rows from the Sheety API response, one dict per customer, each expected to include an "email" key (consumed later by NotificationManager.send_emails() in notification_manager.py)."""
        response = requests.get(url=self.users_endpoint, auth=self._authorization)
        data = response.json()
        self.customer_data = data["users"]
        return self.customer_data
