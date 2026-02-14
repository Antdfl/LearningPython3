from bs4 import BeautifulSoup
import os
import requests

os.system('cls')
# with open("./Python100daycourse/bs4-start/website.html") as file:
#     contents = file.read()

# soup = BeautifulSoup(contents, 'html.parser')
# #print(soup.title)
# # print(soup.title.string)
# all_anchor_tags = soup.find_all(name="a")
#print(all_anchor_tags)
# for tag in all_anchor_tags:
#     print(tag.getText())
#     print(tag.get("href"))
#print(soup.prettify())
# heading = soup.find(name="h3", class_="heading")
# print(heading.getText())
# print(heading.name)
# print(heading.get("class"))
# company_url = soup.select_one(selector="p a")
# print(company_url)
# name = soup.select_one(selector="#name")
# print(name)
# name = soup.select_one(selector=".heading")
# print(name)
# headings = soup.select(selector=".heading")
# print(headings)

response = requests.get("https://news.ycombinator.com/")
yc_web_page = response.text
soup = BeautifulSoup(yc_web_page, "html.parser")

articles = soup.find_all(name="span", class_="titleline")   #select(selector="span.titleline a")
article_texts = []
article_links = []
for article in articles:
    article_texts.append(article.getText())
    article_links.append(article.get("href"))

# scores = soup.find_all(name="span", class_="score")
# for score in scores:
#     print(score.getText())
#print(article_texts)

# article_upvotes_full = soup.find_all(name="span", class_="score")
# print(article_upvotes_full)

article_upvotes = [int(score.getText().split()[0]) for score in soup.find_all(name="span", class_="score")]
#print(article_upvotes)
# print(article_links)
# for index in range(len(article_upvotes)):
#     print(f"{index}  Upvotes: {article_upvotes[index]}" f" Article: {article_texts[index]}")
#    article_upvotes[index] = int(article_upvotes[index].split()[0])
#print(article_upvotes)
# max is a built in function that returns the largest item in an iterable or the largest of two or more arguments.
largest_number = max(article_upvotes)
print(largest_number)
# index is a built in function that returns the index of the first occurrence of the specified value.
largest_index = article_upvotes.index(largest_number)
print(largest_index)
print(f"{article_texts[largest_index]} link {article_links[largest_index]} with {largest_number} votes")