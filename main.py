import json
import logging
import os

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from utils.genUsername import check_username_availability
from utils.getUsername import get_username
from utils.deployDocker import deploy, restart
from utils.matrixApi import generatePassword, get_email_from_username, register_user, set_display_name, set_profile
from models import AgentUpdate, BotList, Bots, Duplicate, Item
from utils.superagent import create_workflow, handleWorkflowBots, update_yaml
from prisma import Prisma

# Global Variables
MATRIX_API_URL = os.environ["MATRIX_URL"]
SUPERAGENT_API_URL = os.environ["SUPERAGENT_API_URL"]

app = FastAPI()
prisma = Prisma()
session = AsyncClient(follow_redirects=True)
f = open('data.json')
data = json.load(f)

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
        if item.bot_username != "":
            bot_username = item.bot_username
        else:
            bot_username = check_username_availability("testworkflow")
        reg_result = register_user(
            bot_username, password, item.name)
        logging.info(reg_result)
        owner_id = await get_username(item.email_id)
        env_vars = {
            "HOMESERVER": MATRIX_API_URL,
            "USER_ID": reg_result['user_id'],
            "PASSWORD": password,
            "DEVICE_ID": reg_result['device_id'],
            "SUPERAGENT_URL": SUPERAGENT_API_URL,
            "ID": item.id,
            "API_KEY": item.api_key,
            "TYPE": item.type,
            "OWNER_ID": owner_id,
            "STREAMING" : not item.streaming
        }
        token = reg_result['access_token']
        if item.profile:
            await set_profile(password, homeserver=MATRIX_API_URL, user_id=reg_result['user_id'], profile_url=item.profile)
        deploy_bot = await deploy(username=bot_username, env=env_vars)
        logging.info(deploy_bot)
        await prisma.bot.create({
            'username': owner_id,
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
            'tags': item.tags.split(','),
            'category' : item.category if item.category else "fun",
            'streaming': not item.streaming
        })
        if item.type == "WORKFLOW" and not item.streaming:
            await handleWorkflowBots(SUPERAGENT_API_URL, item.id, item.api_key, session, prisma, item.email_id, owner_id, item.publish_all)
        return {"status": "created", "user_id": reg_result}
    except Exception as e:
        logging.error(e)
        return {"status": f"error: {e}"}


@app.delete("/list/{username}/del")
async def delete_item(item: Item, username: str = Path(..., title="The username", description="Username of the user")):
    items = await prisma.bot.delete(where={
        'id': username
    })
    if item:
        return items
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/list/{username}")
async def get_list(username: str = Path(..., title="The username", description="Username of the user")):
    public = await prisma.bot.find_many(
        where={
            "publish": True
        }
    )
    items = await prisma.bot.find_many(where={
        'username': username
    })
    if items:
        return {"personal": items, "public": public}
    return {"personal": [], "public": public}


@app.get("/agents/{agent_id}")
async def get_bot(agent_id):
    get_bot = await prisma.bot.find_first(
        where={
            "id": agent_id
        }
    )
    return get_bot


@app.get("/bot/{username}")
async def bot_info(username) -> Bots | None:
    info = await prisma.bot.find_first(
        where={
            "bot_username": username
        }

    )
    return info


@app.get("/user/{username}")
async def get_api(username):
    data = await prisma.bot.find_first(
        where={
            "username": username
        }
    )
    if data:
        return data.email_id
    data = await get_email_from_username(username)
    return data


@app.post("/bots/restart/{username}")
async def restart_bot(username):
    bot_data = await prisma.bot.find_first(
        where={
            "bot_username": username
        }
    )
    if bot_data:
        res = await restart(username)
        return res
    raise HTTPException(detail="Username not found",status_code=401)

@app.post("/bots/{room_id}/check")
async def bots_check(botlist: BotList):
    bots_data = await prisma.bot.find_many(
        where={
            "bot_username" : {
                "in" : botlist.bots
            }
        }
    )
    result = { k:False for k in botlist.bots}
    for i in bots_data:
        result[i.bot_username] = True
    return result


@app.post("/bots/update")
async def update_bot(item: AgentUpdate, agent_id):
    get_bot = await prisma.bot.find_first(
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
    get_bot = await prisma.bot.update(
        where={
            "id": agent_id
        },
        data=item.dict(exclude_none=True)
    )
    return get_bot


@app.get('/botlist', response_model=list[Bots])
async def bots_list(tag: str = None):
    if tag is None:
        data = await prisma.bot.find_many(
            where={
                "publish": True
            }
        )
    else:
        data = await prisma.bot.find_many(
            where={
                'tags': {
                    'has_every': [tag]
                }
            },

        )
    return data


@app.get("/public")
async def public_list():
    return data


@app.post("/workflows/{workflowId}/config")
async def save_yaml(workflow_id, item: str):
    await prisma.workflow.upsert(
        where={
            "id": workflow_id
        },
        data={
            "create": {

            }
        }
    )


@app.post('/agent/duplicate/{username}')
async def agent_duplicate(item: Bots):
    get_agent = await prisma.bot.find_first(
        where={
            "id": item.agent_id
        }
    )
    if get_agent.type == "WORKFLOW":
        workflow_data = await prisma.workflow.find_first(
            where={
                "username": item.username
            }
        )
        workflow = await create_workflow(SUPERAGENT_API_URL, item.name, item.description, get_agent.api_key, session)
        update_yaml(SUPERAGENT_API_URL,
                    workflow["id"], get_agent.api_key, workflow_data.yaml, session)
    return True
