import httpx
import os

admin_token = os.environ["AUTH_TOKEN"]

async def get_username(email):
    headers = {'Authorization': admin_token}
    async with httpx.AsyncClient(headers=headers) as client:
        request = await client.get(
            f"https://matrix.pixx.co/_synapse/admin/v1/threepid/email/users/{email}"
        )
    if request.status_code == 200:
        username = await request.json()["user_id"]
        return username
    return None