import requests
from datetime import datetime
import smtplib
import time
# Initialization mail parameters
my_email = "source@gmail.com"
receiver_email = "recipient@gmail.com"
my_password = ""
PORT = 587
mail_body = "Please look up for the International Space ship ISS"

# My zone parameter for sunset/sunrise extraction
MY_LAT = 0  # Your latitude
MY_LONG = 0 # Your longitude
parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0
}

# Get current time
time_now_hour = datetime.now().hour
#time_now_minute = datetime.now().minute
print(f"{time_now_hour}")#:{time_now_minute}")

def is_iss_overhead():
    # Get ISS position
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data_iss_pos = response.json()

    iss_latitude = float(data_iss_pos["iss_position"]["latitude"])
    iss_longitude = float(data_iss_pos["iss_position"]["longitude"])
    print(f"{iss_latitude}, {iss_longitude}")
   
    if (MY_LAT - 5 < iss_latitude < MY_LAT + 5) and (MY_LONG - 5 < iss_longitude < MY_LONG + 5):
        # if all the condition are true send an email.
        print("ISS is approaching")
        return True
    else:
        return False

def is_night():
    # Get sunrise and sunset
    response = requests.get(url="https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    #print(data)
    sunrise_time = int((data["results"]["sunrise"]).split("T")[1].split(":")[0])
    sunset_time = int((data["results"]["sunset"]).split("T")[1].split(":")[0])
    print(f"sunset: {sunset_time} sunrise: {sunrise_time}")
    if time_now_hour > (sunset_time + 2) or time_now_hour < (sunrise_time):
        print("It's dark")
        return True
    else:
        return False

def send_email():
    try:
        with smtplib.SMTP('smtp.gmail.com', port=PORT) as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_password)
            connection.sendmail(from_addr=my_email, to_addrs=receiver_email, msg=f"Subject: ISS is approching\n\n"
                                                                                 f"{mail_body}")
            print("Email sent successfully")
    except smtplib.SMTPNotSupportedError as e:
        print(f"Error: SMTP command not supported. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# If the ISS is close to my current position (function is_iss_overhead())
# and its currently dark (function is_night()),
# then send an email to tell me to look up
# Bonus: run the code every 60 seconds
while True:
    time.sleep(60)
    if is_night() and is_iss_overhead():
        send_email()