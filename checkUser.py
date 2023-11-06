import requests

MATRIX_API_URL = "https://matrix.immagine.ai"

def check_user_in_matrix(userid):
    # Replace with your actual access token
    #headers = {"Authorization": f"Bearer {access_token}"}

    url = f"{MATRIX_API_URL}/_matrix/client/v3/profile/{userid}"
    response = requests.get(url)  #, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
        #return True, data.get("name"), data.get("displayname")
        return True
    else:
        error_data = response.json()
        errcode = error_data.get("errcode")
        print(error_data)
        return False

def register_bot(username,password,display_name):
    body = {
        "auth": {
            "type": "m.login.dummy"
        },
        "device_id": "chatgptbot",
        "initial_device_display_name": display_name,
        "password": password,
        "username": username
    }
    url = f"{MATRIX_API_URL}/_matrix/client/v3/register"
    response = requests.post(url, json=body)
    if (response.status_code == 200) :
        return response.json()
    else:
        return False

