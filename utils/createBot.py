import requests
import random

MATRIX_API_URL = "https://matrix.multi.so"

def generatePassword(n):
    # defining the list of choices of characters.
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$%^&*()"

    # initializing an empty string to store the password.
    password = ""

    for i in range(n):
        # randomly selecting one character and appending it to the resultant password string
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

if __name__ == "__main__":
    password = generatePassword(10)
    res = register_bot("plates",password,"Plate","plate_device")
    print(res)