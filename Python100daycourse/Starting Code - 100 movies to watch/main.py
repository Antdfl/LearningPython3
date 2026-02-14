import requests
from bs4 import BeautifulSoup
import os

os.system('cls')

URL = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"

# Write your code below this line 👇
response = requests.get(URL)
empire_page = response.text
soup = BeautifulSoup(empire_page, "html.parser")
#print(soup.title)

titles = soup.find_all(name="h3", class_="title")
movies = [title.getText() for title in titles]
movies.reverse()
# extract the reverse of the list with the splicer movies = movies[::-1]
#movies = movies[::-1]
#print(movies)
with open("movies.txt", mode="w", encoding="utf-8") as file:
    for movie in movies:
        file.write(f"{movie}\n")
print("Movies have been written to movies.txt")