from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
os.system('cls')

# Keep the brwoser open after the script finishes
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://en.wikipedia.org/wiki/Main_Page")

# article_count = driver.find_elements(By.CSS_SELECTOR, value="#articlecount ul li a")[1]
# print(article_count.text)
#article_count.click()
# all_portals = driver.find_element(By.LINK_TEXT, value="Content portals")
# all_portals.click()

# The search bar on Wikipedia is hidden behind a magnifying glass icon. We need to click on the icon to reveal the search bar before we can interact with it.
magnifier_lens = driver.find_element(By.CLASS_NAME, value="mw-ui-icon-search")
magnifier_lens.click()

# After clicking the magnifying glass icon, the search bar becomes visible and we can interact with it. We can use the send_keys() method to type into the search bar and the Keys.ENTER to submit the search.
search_bar = driver.find_element(By.NAME, value="search")
search_bar.click()
# We can also use the clear() method to clear the search bar before typing a new query.
search_bar.send_keys("Python")
# We can also use the submit() method to submit the search form instead of using Keys.ENTER.
search_bar.send_keys(Keys.ENTER)



#driver.quit()  # Closes the entire browser