import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:

    def __init__(self):
        self.client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

    def send_sms(self, message_body):
        message = self.client.messages.create(
            body=message_body,
            from_=os.environ["TWILIO_ASSIGNED_NUMBER"],
            to=os.environ["TWILIO_TRUSTED_NUMBER"],
        )
        print(message.status)
