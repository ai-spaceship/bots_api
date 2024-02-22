import logging
import httpx
from prisma import Prisma
from prisma.models import User
from utils.genUsername import check_username_availability
import os
from utils.deployBot import start_ecs_task

from utils.matrixApi import generatePassword, register_user

MATRIX_API_URL = os.environ["MATRIX_URL"]
SUPERAGENT_API_URL = os.environ["SUPERAGENT_API_URL"]


async def workflow_steps(superagent_url: str, workflow_id: str, api_key: str, session: httpx.AsyncClient):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    api_url = f"{superagent_url}/api/v1/workflows/{workflow_id}/steps"
    response = await session.get(
        api_url,
        headers=headers,
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()["data"]
    return response.json()


async def handleWorkflowBots(superagent_url, workflow_id: str, api_key, session, prisma: Prisma, email_id):
    workflow_data = await workflow_steps(
        superagent_url, workflow_id, api_key, session)
    for agents in workflow_data:
        agent_id = agents["agentId"]
        get_bot: User = await prisma.user.find_unique(
            where={
                "id": agent_id
            }
        )
        if not get_bot:
            password = generatePassword(12)
            try:
                agent_data = agents["agent"]
                reg_result = register_user(check_username_availability(
                    agent_data["name"]), password, agent_data["name"])
                logging.info(reg_result)
                env_vars = {
                    "HOMESERVER": MATRIX_API_URL,
                    "USER_ID": reg_result['user_id'],
                    "PASSWORD": password,
                    "DEVICE_ID": reg_result['device_id'],
                    "SUPERAGENT_URL": SUPERAGENT_API_URL,
                    "AGENT_ID": agent_id,
                    "API_KEY": api_key
                }
                deploy_bot = start_ecs_task(env_vars)
                logging.info(deploy_bot)
                await prisma.user.create({
                    'username': "",
                    'bot_username': reg_result['user_id'],
                    'password': password,
                    'api_key': api_key,
                    'id': agent_id,
                    'email_id': email_id,
                    'name': agent_data["name"],
                    'desc': agent_data["description"],
                    'profile_photo':agent_data["avatar"] if agent_data["avatar"] else "",
                    'access_token': reg_result['access_token'],
                    'type': "AGENT",
                    'publish': False,
                    'tags': [agent_data["name"]]
                })
            except Exception as e:
                logging.error(e)
                return False
    return True
