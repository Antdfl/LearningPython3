import requests
from datetime import datetime
import os

APP_ID = os.environ.get("APP_ID", "APP_ID key does not exists")
APP_KEY = os.environ.get("APP_KEY", "APP_KEY key does not exists")
YOUR_WEIGHT = os.environ.get("YOUR_WEIGHT", "YOUR_WEIGHT key does not exists")
YOUR_HEIGHT = os.environ.get("YOUR_HEIGHT", "YOUR_HEIGHT key does not exists")
YOUR_AGE = os.environ.get("YOUR_AGE", "YOUR_AGE does not key exists")
YOUR_GENDER = os.environ.get("YOUR_GENDER", "YOUR_GENDER key does not exists")
BASE_URL = os.environ.get("BASE_URL", "BASE_URL key does not exists")

URL_SHEETY_ENDPOINT = os.environ.get("URL_SHEETY_ENDPOINT", "URL_SHEETY_ENDPOINT key does not exists")
APP_SHEETY_BEARER = os.environ.get("APP_SHEETY_BEARER", "APP_SHEETY_BEARER key does not exists")

exercise_text = input("Tell what exercise you did today? ")
exercise_list = exercise_text.split("and")
print(exercise_list)
# Test whether the 100 day of Python API works before start any API usage.
# response = requests.get(url=URL_TEST)
# response.raise_for_status()
# print(response.json())
url_exercise = f"{BASE_URL}/v1/nutrition/natural/exercise"
headers = {
    "Content-Type": "application/json",
    "x-app-id": APP_ID,
    "x-app-key": APP_KEY
}

today_date = (datetime.now()).strftime("%d/%m/%Y")
now_time = (datetime.now()).strftime("%H:%M:%S")

# We invoke n times the api for getting exercise data, one time for each exercise
exercises = []
for exercise in exercise_list:
    user_params = {
        "query": exercise,
        "weight_kg": int(YOUR_WEIGHT),
        "height_cm": int(YOUR_HEIGHT),
        "age": int(YOUR_AGE),
        "gender": YOUR_GENDER,
    }
    response = requests.post(url=url_exercise, headers=headers, json=user_params)
    result = response.json()
    exercises.append(result)
print(exercises)

#bearer or token authentication
header2 = {
    "Content-Type": "application/json",
    "Authorization": APP_SHEETY_BEARER
}

for exercise in exercises:
    sheet_inputs = {
        "workout": {
            "date": today_date,
            "time": now_time,
            "exercise": (exercise["exercises"][0]["name"]).title(),
            "duration": exercise["exercises"][0]["duration_min"],
            "calories": exercise["exercises"][0]["nf_calories"]
        }
    }
    #print(sheet_inputs)
    response = requests.post(url=URL_SHEETY_ENDPOINT, json=sheet_inputs, headers=header2)
    result = response.json()
    print(result)
