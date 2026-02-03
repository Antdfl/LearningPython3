import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from a .env file if present.
load_dotenv()

class NotificationManager:

    def __init__(self):
        # Create a Twilio client using credentials from environment variables.
        self.client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

    def send_sms(self, message_body):
        # Send an SMS message using the configured Twilio phone numbers.
        message = self.client.messages.create(
            body=message_body,
            from_=os.environ["TWILIO_ASSIGNED_NUMBER"],
            to=os.environ["TWILIO_TRUSTED_NUMBER"],
        )
        # Print delivery status for debugging/verification.
        print(message.status)
