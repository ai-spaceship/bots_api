import logging

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware


from prisma import Prisma

from utils.deployBot import start_ecs_task
from utils.createBot import get_access_token, get_email_from_username, register_bot, generatePassword
from models import Item, Users

app = FastAPI()
prisma = Prisma()

origins = [
    "https://agispace.co",
    "https://super.agispace.co"
]

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
        reg_result = register_bot(
            item.bot_username, password, item.bot_username, f"superagent_{item.agent_name}")
        logging.info(reg_result)
        env_vars = {
                "HOMESERVER": "https://matrix.agispace.co",
                "USER_ID": reg_result['user_id'],
                "PASSWORD": password,
                "DEVICE_ID": reg_result['device_id'],
                "SUPERAGENT_URL": "https://api.agispace.co",
                "AGENT_ID": item.agent_id,
                "API_KEY": item.api_key
        }

        deploy_bot = start_ecs_task(env_vars)
        logging.info(deploy_bot)
        await prisma.user.create({
            'username': item.username,
            'bot_username': reg_result['user_id'],
            'password' : password,
            'api_key': item.api_key,
            'agent_id': item.agent_id,
            'email_id': item.email_id,
            'agent_name': item.agent_name,
            'agent_desc': item.agent_desc,
            'profile_photo': item.profile if item.profile else "",
            'access_token' : get_access_token(reg_result['user_id'],password)
        })
        return {"status" : "created","user_id": reg_result}
    except Exception as e:
        logging.error(e)
        return {"status" : f"error: {e}"}


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
        where= {
            "agent_id" : agent_id
        }
    )
    return get_bot

@app.get('/list')
async def bots_list(tag: str = None):
    if tag is None:
        data = await prisma.bots.find_many(
            include= {
                'meta' : True
            }
        )
    else:
        data = await prisma.bots.find_first(
            where = {
                'meta': {
                        'tags' : {
                            'has_every' : [tag]
                        }
                }
            },
            include= {
                'meta' : True
            }
        )
    return data

@app.get('/get_list/enterprise')
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
                            "bot_id": "@bot_finance:agispace.co",
                            "bot_name": "FinanceBot",
                            "description": "An enterprise finance bot for real-time financial analysis."
                        }
                    ],
                    "popular_rooms" : [
                        {
                            "room_id" : "#trading:agispace.co",
                            "room_name" : "Trading",
                            "description" : "A room for aspiring traders."
                        }
                    ]
                },
                {
                    "title": "Productivity",
                    "popular_bots": [
                        {
                            "bot_id": "@bot_productivity:agispace.co",
                            "bot_name": "ProductivityBot",
                            "description": "Boost your team's productivity with task management and reminders."
                        }
                    ],
                    "popular_rooms" : [
                        {
                            "room_id" : "#Pomodoro:agispace.co",
                            "room_name" : "Pomodoro",
                            "description" : "A room for Productivity enthusiasts."
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


@app.get('/get_list/community')
async def get_list():
    return {
        "data": {
            "categories": [
                {
                    "title": "Entertainment",
                    "popular_bots": [
                        {
                            "bot_id": "@bot_entertainment:agispace.co",
                            "bot_name": "TriviaBot",
                            "description": "Challenge yourself with fun trivia questions and quizzes."
                        }
                    ],
                    "popular_rooms" : [
                        {
                            "room_id" : "#Music:agispace.co",
                            "room_name" : "Music",
                            "description" : "A room for music lovers."
                        }
                    ]
                },
                {
                    "title": "Language",
                    "popular_bots": [
                        {
                            "bot_id": "@bot_language:agispace.co",
                            "bot_name": "TranslatorBot",
                            "description": "Translate between languages with ease using this bot."
                        }
                    ],
                    "popular_rooms" : [
                        {
                            "room_id" : "#Klingon:agispace.co",
                            "room_name" : "Klingon",
                            "description" : "Learn Klingon with AI bots."
                        }
                    ]
                }
                # Add more community categories here...
            ],
            "category_keys": [
                "Entertainment",
                "Language"
                # Add more community category keys here...
            ]
        }
    }
