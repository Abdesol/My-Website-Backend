import requests
import json

from requests import auth
"""
title = "Robert Assistant"
desc = "This project is made for programmers. It makes programmers work more efficient.\nIt have alarm, code saving for copying it, task manager, translation and more services\nFor more information about the code click on View on github."
github = "https://github.com/Champions-clan/Robert-Assistant"
img_name = "robert_logo.png"
img = open(img_name, "rb") 

response = requests.post(
    "http://127.0.0.1/upload_project_img",
    auth=("admin", "password"),
    files={"img":img}
    )
r = response.json()
print(r)

data = {
    "title":title,
    "description":desc,
    "url":github,
    "img_name":r["name"]
}

response2 =  requests.post(
    "http://127.0.0.1/create_project",
    auth=("admin", "password"),
    json=data
)

print(response2.json())
response = requests.post(
    "http://127.0.0.1/delete_project",
    auth=("admin", "password"),
    json={"id":2}
    )
r = response.json()
print(r)
"""

data = {
    "id":1,
    "title":"This is modified",
    "description":"",
    "url":"",
    "img_name":""
}
response = requests.post(
    "http://127.0.0.1/edit_project",
    auth=("admin", "password"),
    json=data
    )
r = response.json()
print(r)