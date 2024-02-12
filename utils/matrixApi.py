from io import BytesIO
import requests
import random
import os
from nio import AsyncClient

MATRIX_API_URL = "https://matrix.pixx.co"

def generatePassword(n):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$%^&*()"
    password = ""

    for i in range(n):
        password += random.choice(characters)

    # finally returning the randomly generated password.
    return password

def register_bot(username,password,display_name,device_id):
    body = {
        "auth": {
            "type": "m.login.dummy"
        },
        "device_id": device_id,
        "initial_device_display_name": display_name,
        "password": password,
        "username": username
    }
    url = f"{MATRIX_API_URL}/_matrix/client/v3/register"
    response = requests.post(url, json=body)
    print(response.json())
    if (response.status_code == 200) :
        return response.json()
    else:
        return {"status" : response.status_code}
    
def get_email_from_username(username):
    auth_token = os.environ["AUTH_TOKEN"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    req = requests.get(f'{MATRIX_API_URL}/_synapse/admin/v2/users/{username}', headers=headers)
    print(req.status_code)
    if req.status_code == 200:
        data = req.json()
        print(data)
        if data["threepids"] is not []:
            return data["threepids"][0]["address"]
    return None

def get_access_token(username,password):
    body= {
    "identifier": { "type": "m.id.user", "user": username },
  
    "password": password,
  
    "type": "m.login.password",
    "device_id": "deployer"
    }
    url = f"{MATRIX_API_URL}/_matrix/client/r0/login"
    response = requests.post(url, json=body)
    if response.status_code == 200:
        return response.json()['access_token']
    
async def set_profile(access_token, homeserver, user_id, profile_url):
    client = AsyncClient(homeserver, user_id)
    await client.login(token=access_token)
    data = requests.get(profile_url)
    upload_img = BytesIO(data.content)
    profile_mxc = await client.upload(upload_img, content_type=data.headers['Content-Type'])
    response = await client.set_avatar(profile_mxc)
    return response