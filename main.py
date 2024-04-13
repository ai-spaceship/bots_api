import logging
import os

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from utils.deployDocker import deploy
from utils.matrixApi import get_email_from_username, generatePassword, register_user, set_display_name, set_profile
from models import Agent, AgentUpdate, Bots, Item
from utils.superagent import handleWorkflowBots
from prisma import Prisma

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
            item.bot_username, password, item.name)
        logging.info(reg_result)
        env_vars = {
            "HOMESERVER": MATRIX_API_URL,
            "USER_ID": reg_result['user_id'],
            "PASSWORD": password,
            "DEVICE_ID": reg_result['device_id'],
            "SUPERAGENT_URL": SUPERAGENT_API_URL,
            "ID": item.id,
            "API_KEY": item.api_key,
            "TYPE" : item.type
        }
        token = reg_result['access_token']
        if item.profile:
            await set_profile(password, homeserver=MATRIX_API_URL, user_id=reg_result['user_id'], profile_url=item.profile)
        deploy_bot = deploy(username=item.bot_username, env=env_vars)
        logging.info(deploy_bot)
        await prisma.user.create({
            'username': "",
            'bot_username': reg_result['user_id'],
            'password': password,
            'api_key': item.api_key,
            'id': item.id,
            'email_id': item.email_id,
            'name': item.name,
            'desc': item.description,
            'profile_photo': item.profile if item.profile else "",
            'access_token': token,
            'type': item.type,
            'publish': item.publish,
            'tags': item.tags.split(',')
        })
        if item.type == "WORKFLOW":
            await handleWorkflowBots(SUPERAGENT_API_URL, item.id, item.api_key, session, prisma, item.email_id)
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
async def get_list(username: str = Path(..., title="The username", description="Username of the user")):
    get_email = get_email_from_username(username)
    public  = await prisma.user.find_many(
        where={
            "publish": True
        }  
    )
    if get_email is not None:
        items = await prisma.user.find_many(where={
            'email_id': get_email
        })
        return {"personal" : items, "public" : public}
    return {"personal": [], "public" : public}


@app.get("/agents/{agent_id}")
async def get_bot(agent_id):
    get_bot = await prisma.user.find_first(
        where={
            "id": agent_id
        }
    )
    return get_bot

@app.get("/bot/{username}")
async def bot_info(username) -> Bots | None:
    info = await prisma.user.find_first(
        where={
            "bot_username" : username
        }
        
    )
    return info


@app.post("/bots/update")
async def update_bot(item: AgentUpdate, agent_id):
    get_bot = await prisma.user.find_first(
        where={
            "id": agent_id
        }
    )
    if get_bot:
        if item.avatar_mxc:
                get_mxc = await set_profile(get_bot.password, homeserver=MATRIX_API_URL, user_id=get_bot.bot_username, profile_url=item.avatar_mxc)
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
        data = await prisma.user.find_many(
            where={
                "publish": True
            }
        )
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

