from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
GYM_URL = "https://appbrewery.github.io/gym/"
ACCOUNT_EMAIL = os.getenv("ACCOUNT_EMAIL")  # The email you registered with
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")      # The password you used during registration

# Clear the console before running the script
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
clear_console()

# Keep the browser open after the script finishes
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)


login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "login-button"))  
)
login_button.click()

email_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "email-input"))
)
email_input.click()
email_input.send_keys(ACCOUNT_EMAIL)

password_input =  WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "password-input"))
)
password_input.click()
password_input.send_keys(ACCOUNT_PASSWORD)

login_button =  WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "submit-button"))
)
login_button.click()

# Detect current day of week
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "schedule-page")))

class_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']")
#print(class_cards)
for card in class_cards:
    #print(card.text)
    day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]")
    day_title = day_group.find_element(By.TAG_NAME, "h2").text
    day_of_week = day_title.split(',')[0]  # Extract the day of the week (e.g., "Monday", "Tuesday", etc.)
    #print(day_of_week)
    if "Tue" in day_title:
        # Check if this is a 6pm class
        time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text
        if "6:00 PM" in time_text:
            # Get the class name
            class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text

            # Find and click the book button
            button = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")
            button.click()

            print(f"✓ Booked: {class_name} on {day_title}")
    




# Keep the browser open after the script finishes
#driver.quit()  # Closes the entire browser
