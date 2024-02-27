import logging
import os

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from httpx import AsyncClient

from utils.deployBot import start_ecs_task
from utils.matrixApi import get_access_token, get_email_from_username, generatePassword, register_user, set_display_name, set_profile
from models import Agent, AgentUpdate, Bot, Bots, Item, Users, WorkflowItem
from utils.superagent import handleWorkflowBots

#Global Variables
MATRIX_API_URL = os.environ["MATRIX_URL"]
SUPERAGENT_API_URL = os.environ["SUPERAGENT_API_URL"]

app = FastAPI()
prisma = Prisma()
session = AsyncClient(follow_redirects=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(request)
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    await prisma.connect()


@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()


@app.post("/add")
async def add_item(item: Item):
    password = generatePassword(10)
    try:
        reg_result = register_user(
            item.bot_username, password, item.agent_name)
        logging.info(reg_result)
        env_vars = {
            "HOMESERVER": MATRIX_API_URL,
            "USER_ID": reg_result['user_id'],
            "PASSWORD": password,
            "DEVICE_ID": reg_result['device_id'],
            "SUPERAGENT_URL": SUPERAGENT_API_URL,
            "AGENT_ID": item.agent_id,
            "API_KEY": item.api_key
        }
        token = reg_result['access_token']
        if item.profile:
            await set_profile(password, homeserver=MATRIX_API_URL, user_id=reg_result['user_id'], profile_url=item.profile)

        deploy_bot = start_ecs_task(env_vars)
        logging.info(deploy_bot)
        await prisma.user.create({
            'username': "",
            'bot_username': reg_result['user_id'],
            'password': password,
            'api_key': item.api_key,
            'id': item.agent_id,
            'email_id': item.email_id,
            'name': item.agent_name,
            'desc': item.agent_desc,
            'profile_photo': item.profile if item.profile else "",
            'access_token': token,
            'type': "AGENT",
            'publish': item.publish,
            'tags': item.tags.split(',')
        })
        return {"status": "created", "user_id": reg_result}
    except Exception as e:
        logging.error(e)
        return {"status": f"error: {e}"}


@app.post("/add/workflows")
async def add_item(item: WorkflowItem):
    password = generatePassword(10)
    try:
        reg_result = register_user(
            item.bot_username, password, item.workflow_name)
        logging.info(reg_result)
        env_vars = {
            "HOMESERVER": MATRIX_API_URL,
            "USER_ID": reg_result['user_id'],
            "PASSWORD": password,
            "DEVICE_ID": reg_result['device_id'],
            "SUPERAGENT_URL": SUPERAGENT_API_URL,
            "WORKFLOW_ID": item.workflow_id,
            "API_KEY": item.api_key
        }

        deploy_bot = start_ecs_task(env_vars)
        logging.info(deploy_bot)
        await prisma.user.create({
            'username': "",
            'bot_username': reg_result['user_id'],
            'password': password,
            'api_key': item.api_key,
            'id': item.workflow_id,
            'email_id': item.email_id,
            'name': item.workflow_name,
            'desc': item.workflow_desc,
            'profile_photo': item.profile if item.profile else "",
            'access_token': reg_result['access_token'],
            'type': "WORKFLOW",
            'publish': item.publish,
            'tags': item.tags.split(',')
        })
        await handleWorkflowBots(SUPERAGENT_API_URL, item.workflow_id, item.api_key, session, prisma, item.email_id)
        return {"status": "created", "user_id": reg_result}
    except Exception as e:
        logging.error(e)
        return {"status": f"error: {e}"}


@app.delete("/list/{username}/del")
async def delete_item(item: Item, username: str = Path(..., title="The username", description="Username of the user")):
    items = await prisma.user.delete(where={
        'id': username
    })
    if item:
        return items
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/list/{username}")
async def get_list(username: str = Path(..., title="The username", description="Username of the user")) -> list[Users]:
    get_email = get_email_from_username(username)
    if get_email is not None:
        items = await prisma.user.find_many(where={
            'email_id': get_email
        })
        return items
    return []


@app.get("/agents/{agent_id}")
async def get_bot(agent_id):
    get_bot = await prisma.user.find_first(
        where={
            "id": agent_id
        }
    )
    return get_bot

@app.get("/bot/{username}")
async def bot_info(username) -> Bot:
    info = await prisma.user.find_first(
        where={
            "bot_username" : username
        }
        
    )
    return info


@app.post("/bots/update")
async def update_bot(item: AgentUpdate, agent_id):
    if item.avatar:
            get_mxc = await set_profile(get_bot.password, homeserver=MATRIX_API_URL, user_id=get_bot.bot_username, profile_url=item.avatar)
            item.avatar_mxc = get_mxc
    if item.name:
        await set_display_name(get_bot.password, homeserver=MATRIX_API_URL, user_id=get_bot.bot_username, name=item.name)
    get_bot = await prisma.user.update(
        where={
            "id": agent_id
        },
        data=item.dict(exclude_none=True)
    )
    return get_bot


@app.get('/botlist')
async def bots_list(tag: str = None) -> list[Bots]:
    if tag is None:
        data = await prisma.user.find_many()
    else:
        data = await prisma.user.find_first(
            where={
                'tags': {
                    'has_every': [tag]
                }
            }
        )
    return data


@app.post('/agent/duplicate')
async def agent_duplicate(item: Agent):
    email_id = get_email_from_username(item.username)
    get_agent = await prisma.user.find_first(
        where={
            "id" : item.agent_id
        }
    )
    return True

