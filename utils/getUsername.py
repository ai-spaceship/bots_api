import httpx
import os

admin_token = os.environ["AUTH_TOKEN"]

async def get_username(email):
    headers = {'Authorization': f"Bearer {admin_token}"}
    async with httpx.AsyncClient(headers=headers) as client:
        request = await client.get(
            f"https://matrix.pixx.co/_synapse/admin/v1/threepid/email/users/{email}"
        )
    if request.status_code == 200:
        username = request.json()
        return username["user_id"]
    return ""

if __name__ == "__main__":
    import asyncio
    data = asyncio.run(get_username("test@pixx.co"))
    print(data)