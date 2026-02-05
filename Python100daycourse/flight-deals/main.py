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
# ==================== Set up the Flight Search ====================
data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()
# Set your origin airport
ORIGIN_CITY_IATA = "LON"
time.sleep(20)
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
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))


for destination in sheet_data:
    # Search for direct flights
    print(f"Getting data for {destination['city']}....")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination['iataCode'],
        from_time=tomorrow,
        to_time=six_month_from_today
    )
    #print(f"flights {flights}")
    cheapest_flight = find_cheapest_flight(flights)
    print(f"{destination['city']}: £{cheapest_flight.price}")

    # ==================== Search for indirect flight if N/A ====================
    if  cheapest_flight.price == "N/A":
        print(f"No direct flight to {destination['city']}. Looking for indirect flights...")
        stopover_flights = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination['iataCode'],
            from_time=tomorrow,
            to_time=six_month_from_today,
            is_direct=False
        )
        cheapest_flight = find_cheapest_flight(stopover_flights)
        print(f"{destination['city']}: £{cheapest_flight.price}")

    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        #     notification_manager.send_sms(
        #         message_body=f"Low price alert! Only £{cheapest_flight.price} to fly "
        #                      f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
        #                      f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}.")
        # Slowing down requests to avoid rate limit
        #
        # In your main.py, craft a different message depending on whether
        # the flight is direct or has a stopover.
        if cheapest_flight.stops == 0:
            message_body = f"Low price alert! Only £{cheapest_flight.price} to fly " \
                           f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, " \
                           f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        else:
            message_body = f"Low price alert! Only £{cheapest_flight.price} to fly " \
                           f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, " \
                           f"on {cheapest_flight.out_date} until {cheapest_flight.return_date} with {cheapest_flight.stops} stop(s)."
        customer_email_list = data_manager.get_customer_emails()
        notification_manager.send_emails(message_body, customer_email_list)

    time.sleep(2)


