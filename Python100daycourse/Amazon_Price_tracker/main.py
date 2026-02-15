from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests
import smtplib

os.system('cls')

load_dotenv()

EMAIL_SERVER = os.environ["EMAIL_SERVER"]
EMAIL_PORT = int(os.environ["EMAIL_PORT"])
EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
URL = "https://appbrewery.github.io/instant_pot/"
price_threshold = 100.00

def send_email(email_body):
        # Create a secure SSL connection and send email
        with smtplib.SMTP(EMAIL_SERVER, port=EMAIL_PORT) as connection:
            connection.starttls()
            connection.login(user=EMAIL_SENDER, password=EMAIL_APP_PASSWORD)
            try:
                connection.sendmail(
                from_addr=EMAIL_SENDER,
                to_addrs=recipient_email,
                msg=f"Subject:Amazon Price Alert!\n\n{email_body}".encode('utf-8')
                )
                print(f"Email sent to {recipient_email}")
            except Exception as e:
                print(f"Failed to send email to {recipient_email}. Error: {e}")


recipient_email = input("Enter the recipient's email address: ")
headers = {
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,it-IT;q=0.7,it;q=0.6", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
}


response = requests.get(URL, headers=headers)
amazon_page = response.text
soup = BeautifulSoup(amazon_page, "html.parser")
#print(soup.prettify())

price_whole = soup.find(name="span", class_="a-price-whole").getText()
price_decimal = soup.find(name="span", class_="a-price-fraction").getText()
price = float(price_whole + price_decimal)
product = soup.find(name="span", id="productTitle").getText().strip()
print(f"{product} is currently priced at ${price}")

message_body = f"Price is now ${price}"
if price < price_threshold:
    send_email(message_body)