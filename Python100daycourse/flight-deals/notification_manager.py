import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:

    def __init__(self):
        self.client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        self.email = os.environ["EMAIL_SENDER"]
        self.app_password = os.environ["EMAIL_APP_PASSWORD"]

    def send_sms(self, message_body):
        message = self.client.messages.create(
            body=message_body,
            from_=os.environ["TWILIO_ASSIGNED_NUMBER"],
            to=os.environ["TWILIO_TRUSTED_NUMBER"],
        )
        print(message.status)

    # Is SMS not working for you or prefer whatsapp? Connect to the WhatsApp Sandbox!
    # https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
    def send_whatsapp(self, message_body):
        message = self.client.messages.create(
            from_=f'whatsapp:{os.environ["TWILIO_WHATSAPP_NUMBER"]}',
            body=message_body,
            to=f'whatsapp:{os.environ["TWILIO_TRUSTED_NUMBER"]}'
        )
        print(message.sid)

    # Create a method in the NotificationManager called send_emails() .
    # NOTE: when sending emails, it won't like the "£" symbol, you might get an error like the one below:
    # Use "GBP" instead of the "£" symbol
    def send_emails(self, email_body, customer_data):
        # Create a secure SSL connection and send email
        import smtplib
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.app_password)
            print(customer_data)
            for customer in customer_data:
                recipient_email = customer["email"]
                # add email error management here if needed
                try:
                    connection.sendmail(
                         from_addr=self.email,
                         to_addrs=recipient_email,
                         msg=f"Subject:New Low Price Flight!\n\n{email_body}".encode('utf-8')
                    )
                    print(f"Email sent to {recipient_email}")
                except Exception as e:
                    print(f"Failed to send email to {recipient_email}. Error: {e}")
