from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prisma import Prisma

app = FastAPI()
prisma = Prisma()

origins = [
    "https://multi.so",
    "https://super.multi.so"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    username: str
    bot_username: str
    api_key: str
    agent_name: str
    agent_desc: str
    profile: str

class UserCreate(BaseModel):
    username: str

@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()


@app.post("/add")
async def add_item(item: Item):
    user = await prisma.post.create({
        'username': item.username,
        'bot_username' : item.bot_username,
        'api_key' : item.api_key,
        'agent_name' : item.agent_name,
        'agent_desc' : item.agent_desc,
        'profile_photo' : item.profile
    })
    if user:
        return True
    else:
        return False


@app.delete("/list/{username}/del")
async def delete_item(item: Item,username: str = Path(..., title="The username", description="Username of the user")):
    items = await prisma.post.delete(where={
        'id': username
    })
    if item:
      return items
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/list/{username}")
async def get_list(username: str = Path(..., title="The username", description="Username of the user")):
    items = await prisma.post.find_many(where={
        'username' : username
    })
    if not items:
        raise HTTPException(status_code=404, detail="List is empty")
    return items

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
            "bot_id": "@bot_finance:immagine.ai",
            "bot_name": "FinanceBot",
            "description": "An enterprise finance bot for real-time financial analysis."
          }
        ]
      },
      {
        "title": "Productivity",
        "popular_bots": [
          {
            "bot_id": "@bot_productivity:immagine.ai",
            "bot_name": "ProductivityBot",
            "description": "Boost your team's productivity with task management and reminders."
          }
        ]
      }
      # Add more enterprise categories here...
    ],
    "category_keys": [
      "Finance",
      "Productivity"
      #Add more enterprise category keys here...
    ]
  }
}

@app.get('/get_list/community')
async def get_list():
    return {
  "status": "success",
  "message": "List of bots by community categories",
  "data": {
    "categories": [
      {
        "title": "Entertainment",
        "popular_bots": [
          {
            "bot_id": "@bot_entertainment:immagine.ai",
            "bot_name": "TriviaBot",
            "description": "Challenge yourself with fun trivia questions and quizzes."
          }
        ]
      },
      {
        "title": "Language",
        "popular_bots": [
          {
            "bot_id": "@bot_language:immagine.ai",
            "bot_name": "TranslatorBot",
            "description": "Translate between languages with ease using this bot."
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
