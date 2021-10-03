import requests
from requests import auth

img = open("python.png", "rb")

response1 = requests.post(
    "http://127.0.0.1/upload_file",
    auth=("admin", "password"),
    files={"file":img}
    )
r = response1.json()
print(r)


name = "Python for beginners"
src = r["name"]

data = {
    "name":name,
    "src":src
}

response2 =  requests.post(
    "http://127.0.0.1/create_certificate",
    auth=("admin", "password"),
    json=data
)

print(response2.json())