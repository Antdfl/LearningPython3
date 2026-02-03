# This file coordinates the app: data loading, flight search, and notifications.
import requests
from datetime import datetime
import os
import time
from datetime import datetime, timedelta
from pprint import pprint
from flight_search import FlightSearch
from data_manager import DataManager
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager
# Imports: stdlib utilities, then app-specific modules for flights, data, and notifications.
# ==================== Set up the Flight Search ====================
# Create helper objects for the program workflow.
data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()
# Set your origin airport
ORIGIN_CITY_IATA = "LON"

# Load destination data (city, IATA code, lowest price) from the data source.
sheet_data  = data_manager.get_destination_data()

# ==================== Update the Airport Codes in Google Sheet ====================
# for row in sheet_data:
#     if row["iataCode"] == "":
#         row["iataCode"] = flight_search.get_destination_code(row["city"])
#         # slowing down requests to avoid rate limit
#         time.sleep(2)
# print(f"sheet_data:\n {sheet_data}")
#
# data_manager.destination_data = sheet_data
# data_manager.update_destination_codes()

# ==================== Search for Flights ====================
# Define the search window: from tomorrow up to ~6 months out.
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

for destination in sheet_data:
    # Query flight offers for each destination in the sheet.
    print(f"Getting data for {destination['city']}....")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination['iataCode'],
        from_time=tomorrow,
        to_time=six_month_from_today
    )
    print(f"flights {flights}")
    # Extract the cheapest flight from the API response.
    cheapest_flight = find_cheapest_flight(flights)
    print(f"{destination['city']}: £{cheapest_flight.price}")
    # Send an SMS alert if this flight beats the stored lowest price.
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        notification_manager.send_sms(
            message_body=f"Low price alert! Only £{cheapest_flight.price} to fly "
                         f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
                         f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}.")
    # Slowing down requests to avoid rate limit
    time.sleep(2)


