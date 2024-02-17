import logging

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
#from dotenv import load_dotenv

#load_dotenv()

from prisma import Prisma

from utils.deployBot import start_ecs_task
from utils.matrixApi import get_access_token, get_email_from_username, generatePassword, register_user, set_display_name, set_profile
from models import Agent, AgentUpdate, Bots, Item, Users, WorkflowItem

app = FastAPI()
prisma = Prisma()

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
        print(reg_result)
        logging.info(reg_result)
        env_vars = {
            "HOMESERVER": "https://matrix.pixx.co",
            "USER_ID": reg_result['user_id'],
            "PASSWORD": password,
            "DEVICE_ID": reg_result['device_id'],
            "SUPERAGENT_URL": "https://api.pixx.co",
            "AGENT_ID": item.agent_id,
            "API_KEY": item.api_key
        }
        token = reg_result['access_token']
        if item.profile:
            await set_profile(password, homeserver="https://matrix.pixx.co", user_id=reg_result['user_id'], profile_url=item.profile)

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
            item.bot_username, password, item.agent_name)
        logging.info(reg_result)
        env_vars = {
            "HOMESERVER": "https://matrix.pixx.co",
            "USER_ID": reg_result['user_id'],
            "PASSWORD": password,
            "DEVICE_ID": reg_result['device_id'],
            "SUPERAGENT_URL": "https://api.pixx.co",
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
            'access_token': get_access_token(reg_result['user_id'], password),
            'type': "WORKFLOW",
            'publish': item.publish,
            'tags': item.tags.split(',')
        })
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


@app.post("/bots/update")
async def update_bot(item: AgentUpdate, agent_id):
    get_bot = await prisma.user.update(
        where={
            "id": agent_id
        },
        data={
            "desc": item.description,
            "profile_photo": item.avatar,
            "name" : item.name
        }
    )
    if item.avatar:
            await set_profile(get_bot.password, homeserver="https://matrix.pixx.co", user_id=get_bot.bot_username, profile_url=item.avatar)
    if item.name:
        await set_display_name(get_bot.password, homeserver="https://matrix.pixx.co", user_id=get_bot.bot_username, name=item.name)
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
    return True


@app.get('/botlist/enterprise')
async def get_list():
    return {
        "status": "success",
        "message": "List of bots by enterprise categories",
        "data": {
            "categories": [
                {
                    "title": "Finance",
                    "popular_bots": [
                        {
                             "author": "@bot_finance:pixx.co",
                             "bot_username": "@bot_finance:pixx.co",
                             "desc": "An enterprise finance bot for real-time financial analysis.",
                             "name": "FinanceBot",
                             "tags": ["finance", "analysis", "real-time"],
                             "id": "ed15f86a-50f4-4db2-a1f4-4e7b8d51b530",
                             "type": "Finance"
                        }
                    ],
                    "popular_rooms": [
                        {
                            "author": "@bot_finance:pixx.co",
                            "room_id": "#Pomodoro:pixx.co",
                            "desc": "An enterprise finance bot for real-time financial analysis.",
                            "name": "FinanceBot",
                            "tags": ["finance", "analysis", "real-time"],
                            "id": "ed15f86a-50f4-4db2-a1f4-4e7b8d51b530",
                            "type": "Finance"
                        }
                    ]
                },
                {
                    "title": "Productivity",
                    "popular_bots": [
                        {
                             "author": "@bot_productivity:pixx.co",
                             "bot_username": "@bot_productivity:pixx.co",
                             "desc": "Boost your team's productivity with task management and reminders.",
                             "name": "ProductivityBot",
                             "tags": ["productivity", "task management", "reminders"],
                             "id": "8eb6419b-7f6d-4c5e-884b-042f2b6cf460",
                             "type": "Finance"
                        }
                    ],
                    "popular_rooms": [
                        {
                            "author": "@bot_productivity:pixx.co",
                            "room_id": "#Pomodoro:pixx.co",
                            "desc": "Boost your team's productivity with task management and reminders.",
                            "name": "ProductivityBot",
                            "tags": ["productivity", "task management", "reminders"],
                            "id": "8eb6419b-7f6d-4c5e-884b-042f2b6cf460",
                            "type": "Finance"
                        }
                    ]
                }
                # Add more enterprise categories here...
            ],
            "category_keys": [
                "Finance",
                "Productivity"
                # Add more enterprise category keys here...
            ]
        }
    }


@app.get('/botlist/community')
async def get_list():
    return {
        "data": {
            "categories": [
                {
                    "title": "Health",
                    "popular_bots": [
                        {
                            "author": "@bot_health:pixx.co",
                            "bot_username": "@bot_health:pixx.co",
                            "desc": "Monitor your health metrics and provide personalized health tips.",
                            "name": "HealthBot",
                            "tags": ["health", "monitoring", "personalized tips"],
                            "id": "614d743e-2f65-4c9b-910b-7d66a9f2049b",
                            "type": "Health"
                        }
                    ],
                    "popular_rooms": [
                        {
                            "author": "@bot_health:pixx.co",
                            "room_id": "#bot_health:pixx.co",
                            "desc": "Monitor your health metrics and provide personalized health tips.",
                            "name": "HealthBot",
                            "tags": ["health", "monitoring", "personalized tips"],
                            "id": "614d743e-2f65-4c9b-910b-7d66a9f2049b",
                            "type": "Health"
                        }
                    ]
                },
                {
                    "title": "Business",
                    "popular_bots": [
                        {
                            "author": "@bot_hr:pixx.co",
                            "bot_username": "@bot_hr:pixx.co",
                            "desc": "Streamline your HR processes with automated onboarding and employee management.",
                            "name": "HRBot",
                            "tags": ["HR", "onboarding", "employee management"],
                            "id": "6a14b065-9a2e-4d2c-bacd-b1a2d382140c",
                            "type": "Business"
                        }
                    ],
                    "popular_rooms": [
                        {
                            "author": "@bot_hr:pixx.co",
                            "bot_username": "#bot_hr:pixx.co",
                            "desc": "Streamline your HR processes with automated onboarding and employee management.",
                            "name": "HRBot",
                            "tags": ["HR", "onboarding", "employee management"],
                            "id": "6a14b065-9a2e-4d2c-bacd-b1a2d382140c",
                            "type": "Business"
                        }
                    ]
                }
                # Add more community categories here...
            ],
            "category_keys": [
                "Health",
                "Business"
                # Add more community category keys here...
            ]
        }
    }
