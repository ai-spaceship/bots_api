import requests
import random
import re
import os

MATRIX_API_URL = os.environ["MATRIX_URL"]

def check_username_availability(username, formatted=False):
    # Replace special characters with _
    if not formatted:
        username = re.sub(r'[^\w]', '_', username).lower()

    generate_username = username + str(random.randint(1, 10000))
    # API endpoint
    api_url = f"{MATRIX_API_URL}/_matrix/client/v3/register/available?username={generate_username}"
    
    # Check if the username is available
    response = requests.get(api_url)
    if response.status_code == 200:
        return generate_username
    else:
        # Username is not available, append a random number and try again
        return check_username_availability(username, True)

# Example usage
if __name__ == "__main__":
    input_username = input("Enter preferred username: ")
    import time

    start = time.time()
    available_username = check_username_availability(input_username)
    print("Available username:", available_username)

    end = time.time()
    print(end - start)
