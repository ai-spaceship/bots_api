import aiohttp
import os

docker_ip = os.environ["DOCKER_IP"]

async def deploy(username, env):
    data = {
        'username' : username,
        'env_vars' : env
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{docker_ip}/deploy', json=data) as response:
            if response.status == 200:
                data = await response.json()
            else:
                return None
    
    return data["container_id"]

async def restart(username):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{docker_ip}/restart/{username}") as response:
            if response.status == 200:
                return True
    return False
