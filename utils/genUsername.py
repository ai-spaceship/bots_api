import requests
import random
import re
import os

MATRIX_API_URL = os.environ["MATRIX_URL"]

def check_username_availability(username):
    # Replace special characters with _
    username = re.sub(r'[^\w]', '_', username)

    # API endpoint
    api_url = f"{MATRIX_API_URL}/_matrix/client/v3/register/available?username={username}"
    
    # Check if the username is available
    response = requests.get(api_url)
    data = response.json()

    if data.get('available'):
        return username
    else:
        # Username is not available, append a random number and try again
        new_username = username + '_' + str(random.randint(1, 1000))
        return check_username_availability(new_username)

# Example usage
if __name__ == "__main__":
    input_username = input("Enter preferred username: ")
    available_username = check_username_availability(input_username)
    print("Available username:", available_username)
