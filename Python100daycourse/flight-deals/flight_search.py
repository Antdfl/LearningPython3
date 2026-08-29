"""
flight-deals/flight_search.py

# Purpose: This module defines FlightSearch, a class that queries the
# Amadeus flight-search API: resolving city names to IATA airport codes,
# requesting an OAuth token, and searching flight offers between two cities.
#
# Audience Note for Junior Programmers:
# Credentials AMADEUS_API_KEY/AMADEUS_API_SECRET come from environment
# variables; the OAuth token is fetched once in __init__ and is NOT
# automatically refreshed if it expires during a long-running session.
#
# Dependencies:
# - requests (pip package): HTTP calls to the Amadeus API.
# - python-dotenv (pip package): loads the .env file.
# - datetime (standard library): used only for formatting dates in
#   check_flights.
"""
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
IATA_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations/cities"
FLIGHT_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers"
TOKEN_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"

load_dotenv()

class FlightSearch:
    """This class wraps three Amadeus API endpoints (IATA city lookup, OAuth token, flight offers search) behind three public methods, with the OAuth token obtained once at construction time and stored in self._token."""
    
    #This class is responsible for talking to the Flight Search API.
    def __init__(self):
        """Reads the two Amadeus credentials from environment variables and immediately calls self._get_new_token() to populate self._token before the object is usable.
        
        Parameters:
            None
        
        Returns:
            None
        """
        self._api_key = os.environ["AMADEUS_API_KEY"]
        self._api_secret = os.environ["AMADEUS_API_SECRET"]
        self._token = self._get_new_token()

    def get_destination_code(self, city_name):
        """Looks up a city name's IATA airport code via the Amadeus city-search endpoint. Returns the string "N/A" if the API response has no matching airport (IndexError) and "Not Found" if the response shape is unexpected (KeyError).

        Parameters:
            city_name (str): a city name to search for.

        Returns:
            str: the IATA code on success, or one of the two sentinel strings above on failure.
        """
        print(f"city_name: {city_name}")
        headers = {"Authorization": f"Bearer {self._token}"}
        input_data = {
              "keyword": city_name,
              "max": "2",
              "include": "AIRPORTS"
        }
        response = requests.get(url=IATA_ENDPOINT, params=input_data, headers=headers)
        print(f"Status code {response.status_code}. Airport IATA: {response.text}")
        try:
            code = response.json()["data"][0]['iataCode']
        except IndexError:
            print(f"IndexError: No airport code found for {city_name}.")
            return "N/A"
        except KeyError:
            print(f"KeyError: No airport code found for {city_name}.")
            return "Not Found"
        return code

    def _get_new_token(self):
        """Requests a fresh OAuth2 access token from Amadeus using the client-credentials grant type, stores it in self._token, and returns it.

        Parameters:
            None

        Returns:
            str: the new access token.
        """
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret,
        }
        response = requests.post(url=TOKEN_ENDPOINT, headers=header, data=body)
        #print(f"Your token is {response.json()['access_token']}")
        #print(f"Your token expires in {response.json()['expires_in']} seconds")
        self._token = response.json()["access_token"]
        return self._token

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time, is_direct=True):
        """
        Searches for flight options between two cities on specified departure and return dates
        using the Amadeus API.
        Parameters:
            origin_city_code (str): The IATA code of the departure city.
            destination_city_code (str): The IATA code of the destination city.
            from_time (datetime): The departure date.
            to_time (datetime): The return date.
            is_direct: If a direct flight is not found, search Amadeus one more time for that
        destination to see if there are indirect flights (flights with 1 stop or 2 stops) instead.
        Capture the cheapest flight price for a flight with a stopover.
        Returns:
            dict or None: A dictionary containing flight offer data if the query is successful; None
            if there is an error.
        The function constructs a query with the flight search parameters and sends a GET request to
        the API. It handles the response, checking the status code and parsing the JSON data if the
        request is successful. If the response status code is not 200, it logs an error message and
        provides a link to the API documentation for status code details.
        """
        if is_direct:
            non_stop = "true"
        else:
            non_stop = "false"
        print(f"is direct flight: {non_stop}")
        # print(f"Using this token to check_flights() {self._token}")
        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": from_time.strftime("%Y-%m-%d"),
            "returnDate": to_time.strftime("%Y-%m-%d"),
            "adults": 1,
            "nonStop": non_stop,
            "currencyCode": "GBP",
            "max": "10",
        }

        response = requests.get(
            url=FLIGHT_ENDPOINT,
            headers=headers,
            params=query,
        )

        if response.status_code != 200:
            print(f"check_flights() response code: {response.status_code}")
            print("There was a problem with the flight search.\n"
                  "For details on status codes, check the API documentation:\n"
                  "https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api"
                  "-reference")
            print("Response body:", response.text)
            return None

        return response.json()