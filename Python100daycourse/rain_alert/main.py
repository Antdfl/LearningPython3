import requests
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
client = Client(account_sid, auth_token)

APY_KEY=os.environ.get("OWM_API_KEY")
MY_LAT=1   # fictitious latitude
MY_LONG=2  # fictitious longitude

OWN_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

weather_params = {
    "lat": MY_LAT,
    "lon": MY_LONG,
    "appid": APY_KEY,
    "cnt": 4,
    "units": "metric"
}

response = requests.get(OWN_ENDPOINT, params=weather_params)
response.raise_for_status()
weather_data = response.json()

def umbrella_needed():
    will_rain = False
    for hour_data in weather_data["list"]:
        condition_code = hour_data["weather"][0]["id"]
        #print(condition_code)
        if condition_code < 700:
            will_rain = True
        else:
            will_rain = False
    return will_rain

if umbrella_needed():
    print("Bring an umbrella")
    message = client.messages.create(
        body="It's going to rain today. Bring an umbrella",
        from_="+assigned_number",
        to="+trusted_number",
    )
    print(message.status)
else:
    print("No umbrella needed")
    