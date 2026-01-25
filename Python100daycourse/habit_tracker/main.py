from time import strftime

import requests
from datetime import datetime

TOKEN = "my_invented_token_1234"
USERNAME= "my_invented_username"
pixela_endpoint = "https://pixe.la/v1/users"  # pyright:ignore
GRAPH = "my_graph1"

user_params = {
    "token": TOKEN,
    "username": USERNAME ,
    "agreeTermsOfService": "yes",
    "notMinor" : "yes"
}
# 1st step Create user
# response = requests.post(url=pixela_endpoint, json=user_params)
# print(response.text)

# Create a new graph
graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"
graph_config = {
    "id" : GRAPH,
    "name": "My invented graph",
    "unit": "min",
    "type": "float",
    "color": "shibafu"  #green
}

headers = {
     "X-USER-TOKEN": TOKEN
      }

today = (datetime(year=2026, month=1, day=23)).strftime("%Y%m%d")
#today = datetime.now()
print(today)
# response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
# print(response.text)
pixel_config = {
    "date" : today,
    "quantity": "60"
}

# post_pix_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH}"
# response = requests.post(url=post_pix_endpoint, json=pixel_config, headers=headers)
# print(response.text)
# test URL in my case is https://pixe.la/v1/users/puurome/graphs/study1

pixel_update = {
    "quantity": "40"
}
pixela_update_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH}/{today}"
#response = requests.put(url=pixela_update_endpoint, json=pixel_update, headers=headers)

delete_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH}/{today}"
response = requests.delete(url=delete_endpoint, headers=headers)
print(response.text)
