"""
flight-deals/notification_manager.py

# Purpose: This module defines NotificationManager, a class that sends
# flight-deal alerts to a customer list via three channels: SMS, WhatsApp,
# and email.
#
# Audience Note for Junior Programmers:
# Credentials (Twilio SID/auth token, email sender address, app password)
# are read from environment variables via os.environ and python-dotenv's
# load_dotenv(), never hardcoded - so this module will raise a KeyError at
# class instantiation time if the required .env variables are missing.
#
# Dependencies:
# - twilio (pip package): SMS/WhatsApp via the Twilio REST API.
# - python-dotenv (pip package): loads the .env file.
# - smtplib (standard library, imported locally inside send_emails): the
#   email channel over Gmail's SMTP server.
"""
import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:
    """This class bundles three outbound notification channels (SMS, WhatsApp, email) for sending flight-deal alerts. All communication channels are built on credentials read from environment variables within the __init__ method (including a Twilio client, a sender email address, and an app password). Instantiating this class will raise a KeyError immediately if any required environment variable is missing, as there is no lazy or deferred credential loading."""

    def __init__(self):
        """
        Reads all four required credentials from environment variables and builds the
        Twilio REST client used by send_sms()/send_whatsapp(). Fails fast with a KeyError
        naming the missing variable rather than deferring the failure to whichever method
        is called first.

        Parameters:
            None (reads TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, EMAIL_SENDER,
            EMAIL_APP_PASSWORD from the environment/.env file).

        Returns:
            None.
        """
        self.client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        self.email = os.environ["EMAIL_SENDER"]
        self.app_password = os.environ["EMAIL_APP_PASSWORD"]

    def send_sms(self, message_body):
        """
        Sends a plain SMS via the Twilio REST API, from the number configured in
        TWILIO_ASSIGNED_NUMBER to the single number configured in TWILIO_TRUSTED_NUMBER
        (this project targets one hardcoded recipient, not a customer list).

        Parameters:
            message_body (str): The text content of the SMS.

        Returns:
            None. Prints the message's Twilio delivery status to stdout.
        """
        message = self.client.messages.create(
            body=message_body,
            from_=os.environ["TWILIO_ASSIGNED_NUMBER"],
            to=os.environ["TWILIO_TRUSTED_NUMBER"],
        )
        print(message.status)

    # Is SMS not working for you or prefer whatsapp? Connect to the WhatsApp Sandbox!
    # https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
    def send_whatsapp(self, message_body):
        """
        Sends the same alert as send_sms(), but over Twilio's WhatsApp Sandbox instead of
        plain SMS - both the sender and recipient numbers are prefixed with "whatsapp:" so
        Twilio routes the message through that channel.

        Parameters:
            message_body (str): The text content of the WhatsApp message.

        Returns:
            None. Prints the message's Twilio SID to stdout.
        """
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
        """
        Emails the same alert to every customer in customer_data, one at a time over a
        single Gmail SMTP (STARTTLS) connection. Unlike send_sms()/send_whatsapp(), a
        failure for one recipient (caught per-iteration) does not stop the remaining
        emails from being attempted.

        Parameters:
            email_body (str): The message text, appended after a fixed "New Low Price
                Flight!" subject line.
            customer_data (list[dict]): Customer records, each expected to have an
                "email" key with the recipient address.

        Returns:
            None. Prints a per-recipient success/failure line to stdout.
        """
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
