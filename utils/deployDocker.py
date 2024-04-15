import aiohttp
import os

docker_ip = os.environ["DOCKER_IP"]

async def deploy(username, env):
    data = {
        'username' : username,
        'env_vars' : env
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{docker_ip}:8080/deploy', json=data) as response:
            if response.status == 200:
                data = await response.json()
            else:
                return None
    
    return data["container_id"]
