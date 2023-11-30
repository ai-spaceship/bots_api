import requests
import random
import os

MATRIX_API_URL = "https://matrix.multi.so"

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
    data = req.json()
    if data["threepids"] is not []:
        return data["threepids"][0]["address"]
    return None

if __name__ == "__main__":
    #password = generatePassword(10)
    #res = register_bot("plates",password,"Plate","plate_device")
    #print(res)
    res = get_email_from_username("@jasmindreasond=40skiff.com:multi.so")
    print(res)