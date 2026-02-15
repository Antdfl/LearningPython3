import requests
from bs4 import BeautifulSoup
import os

os.system('cls')

# Create an input to ask the user which year they want to travel to in YYYY-MM-DD format.
date_to_travel = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

URL = f"https://www.billboard.com/charts/hot-100/{date_to_travel}/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

# Write your code below this line 👇
response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
print(soup.title)
song_titles = [song.getText().strip() for song in soup.select(selector="li ul li h3")]
#print(song_titles)
song_artists = [artist.getText().strip() for artist in soup.select(selector="li ul li span a")]
print(song_artists)



# <h3 id="title-of-a-story" class="c-title  a-font-basic u-letter-spacing-0010 u-max-width-397 lrv-u-font-size-16 lrv-u-font-size-14@mobile-max u-line-height-22px u-word-spacing-0063 u-line-height-normal@mobile-max a-truncate-ellipsis-2line lrv-u-margin-b-025 lrv-u-margin-b-00@mobile-max">
# 				Choosin' Texas		
	
# </h3>
