"""
AUTOMATED PRICE MONITORING SCRIPT

This script monitors the price of a specific product (the Instant Pot) on Amazon/AppBrewery
using web scraping and sends an automated email alert if the current price drops below a predefined threshold.

Prerequisites:
1. The 'requests' library and 'beautifulsoup4' must be installed (`pip install requests beautifulsoup4`).
2. Environment variables (EMAIL_SERVER, EMAIL_PORT, etc.) must be set in a .env file for email credentials.
3. A valid User-Agent header is required to mimic a real browser request and prevent blocking.

WORKFLOW:
1. Load environment variables for secure email connection.
2. Define the target URL and price threshold.
3. Scrape the target webpage using BeautifulSoup.
4. Extract the product title, whole price digits, and decimal fraction.
5. Compare the extracted float price against the defined threshold.
6. If the price is lower than the threshold, send an email alert to the specified recipient.
"""
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests
import smtplib

load_dotenv()

EMAIL_SERVER = os.environ["EMAIL_SERVER"]
EMAIL_PORT = int(os.environ["EMAIL_PORT"])
EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
URL = "https://appbrewery.github.io/instant_pot/"
price_threshold = 100.00


def send_email(email_body):
        '''
        Sends a secure, encrypted alert email via SMTP.

        Args:
            email_body (str): The message body detailing the price change.
        Conceptually, this function handles external API interactions and security setup.
        '''
        # Establishing connection details from environment variables is crucial for security.
        try:
            with smtplib.SMTP(EMAIL_SERVER, port=EMAIL_PORT) as connection:
                connection.starttls() # Encrypt the connection for secure login
                connection.login(user=EMAIL_SENDER, password=EMAIL_APP_PASSWORD)

                # Constructing the email message payload
                subject = "Amazon Price Alert!"
                message = f"Subject: {subject}\n\n{email_body}"

                connection.sendmail(
                    from_addr=EMAIL_SENDER,
                    to_addrs=recipient_email,
                    msg=message.encode('utf-8') # Encode the message string to bytes for transmission
                )
                print(f"SUCCESS: Email alert sent successfully to {recipient_email}")
        except Exception as e:
            # Catching general exceptions here is necessary because email failure can occur
            # due to network issues, invalid credentials, or API limits.
            print(f"ERROR: Failed to send email to {recipient_email}. Check .env variables and network connection. Error details: {e}")


def scrape_and_monitor():
        '''
        Core scraping logic. Fetches product data from the target URL, extracts the price,
        and triggers the alert mechanism if the threshold is breached.

        Returns:
            str | None: The extracted product title or None if scraping fails.
        '''
        # 1. Setup Request Headers and Target URL
        headers = {
            "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,it-IT;q=0.7,it;q=0.6",
            # User-Agent must be realistic to avoid being blocked by the server.
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
        }

        # 2. Fetch Page Content
        print("-> Connecting to Amazon/AppBrewery URL and fetching page content...")
        try:
            response = requests.get(URL, headers=headers)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
             print(f"FATAL ERROR: Could not connect to the URL. Please check your internet connection and the target URL ({URL}). Error: {e}")
             return None

        amazon_page = response.text
        soup = BeautifulSoup(amazon_page, "html.parser")

        # 3. Data Extraction (The core scraping logic)
        try:
            price_whole = soup.find(name="span", class_="a-price-whole").getText()
            price_decimal = soup.find(name="span", class_="a-price-fraction").getText()
            # Concatenating whole and decimal parts and converting to float for comparison
            price = float(price_whole + price_decimal)

            product = soup.find(name="span", id="productTitle").getText().strip()
            print("\n==========================================")
            print(f"✅ SUCCESS: Detected Product: {product}")
            print(f"💰 CURRENT PRICE DETECTED: ${price:.2f}")
            print("==========================================\n")

            # 4. Comparison and Action Trigger
            message_body = f"The Instant Pot is currently priced at ${price:.2f}."
            if price < price_threshold:
                print(f"🚨 ALERT TRIGGERED: Price (${price:.2f}) is below the threshold (${price_threshold:.2f}). Sending email alert...")
                send_email(message_body)
            else:
                print(f"ℹ️ INFO: Current price ${price:.2f} is above or equal to the threshold. No alert sent.")

        except AttributeError:
            # This catches errors if one of the required HTML elements (span, id="productTitle") is missing on the page.
            print("⚠️ SCRAPING FAILED: Could not find necessary element classes/IDs. The target website structure may have changed.")
        except ValueError:
             print("⚠️ DATA PARSING ERROR: Failed to convert extracted price components into a float.")
        except Exception as e:
             print(f"❌ UNEXPECTED ERROR during scraping process: {e}")


if __name__ == "__main__":
    # Initial setup and user input handling
    try:
        recipient_email = input("Enter the recipient's email address for alerts: ")
    except EOFError: # Handle cases where input might be redirected or unavailable
         print("\n[SETUP ERROR]: Could not read recipient email. Exiting.")
         exit(1)

    # Run the main scraping and monitoring process
    scrape_and_monitor()

    os.system('cls')
