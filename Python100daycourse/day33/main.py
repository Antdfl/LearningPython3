import requests
from datetime import datetime
# try:
#     response = requests.get(url="http://api.open-notify.org/iss-now.json")
#     print(response.status_code)
# except requests.exceptions.ConnectionError:
#     print("Connection Error")

latitude = 41.902782
longitude = 12.496365
tzid = "Europe/Rome"
parameters = {
    "lat": latitude,
    "lng": longitude,
    "tzid": tzid,
    "formatted": 0
}
response = requests.get(url="https://api.sunrise-sunset.org/json", params=parameters)
response.raise_for_status()
data = response.json()
#print(data)
sunrise_time = (data["results"]["sunrise"]).split("T")[1].split(":")[0]
sunset_time = (data["results"]["sunset"]).split("T")[1].split(":")[0]
print(f"sunrise: {sunrise_time} sunset: {sunset_time}")

time_now_hour = datetime.now().hour
time_now_minute = datetime.now().minute
print(f"{time_now_hour}:{time_now_minute}")