from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
os.system('cls')

# Keep the browser open after the script finishes
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://secure-retreat-92358.herokuapp.com/")

first_name = driver.find_element(By.NAME, value="fName")
first_name.send_keys("Antonio")

last_name_field = driver.find_element(By.NAME, value="lName")
last_name_field.send_keys("DFL")

email_field = driver.find_element(By.NAME, value="email")
email_field.send_keys("p@p.com")

#submit_button = driver.find_element(By.XPATH, value="/html/body/form/button[1]")
submit_button = driver.find_element(By.CSS_SELECTOR, value="form button")
submit_button.click()
