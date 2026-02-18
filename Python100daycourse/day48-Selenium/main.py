from selenium import webdriver
from selenium.webdriver.common.by import By
import os
os.system('cls')

# Keep the brwoser open after the script finishes
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://www.python.org/")

# price_dollar = driver.find_element(By.CLASS_NAME, "a-price-whole").text
# price_cents = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
# print(f"Current price: ${price_dollar}.{price_cents}")

#searchbar = driver.find_element(By.NAME, value="q")
# print(searchbar.tag_name)
# print(searchbar.get_attribute("placeholder"))
#button = driver.find_element(By.ID, value="submit")
# documentation_link = driver.find_element(By.CSS_SELECTOR, value=".documentation-widget a")
# print(documentation_link.text)

# The XPATH is the most powerful way to locate an element, but it is also the slowest. It is recommended to use it as a last resort when other methods fail.
# With the inspection tool, we can find the XPATH of an element by right-clicking on it and selecting "Copy" > "Copy XPATH". However, this method is not recommended as it can be very brittle and may break if the website structure changes. It is better to write your own XPATH that is more robust and less likely to break.
#bug_link = driver.find_element(By.XPATH, value='//*[@id="site-map"]/div[2]/div/ul/li[3]/a')
#print(bug_link.text)

time_events = driver.find_elements(By.CSS_SELECTOR, value='.event-widget time')
event_name = driver.find_elements(By.CSS_SELECTOR, value='.event-widget li a')

#dict_events = {i: {time.text: link.text} for i, (time, link) in enumerate(zip(time_events, event_name))}
event = {}
for n in range(len(time_events)):
    event[n] = {"time": time_events[n].text,
                 "name": event_name[n].text
            }

print(event)
   # print(f"{time.text} - {link.text}")

#driver.close()  # Closes the current tab
driver.quit()  # Closes the entire browser
