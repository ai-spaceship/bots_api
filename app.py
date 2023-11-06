from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import docker
from pydantic import BaseModel
from checkUser import register_bot

class Item(BaseModel):
    botusername: str
    botpassword: str
    botdisplayname: str
    username: str 
    flowise_link: str | None = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()
client = docker.from_env()

class DeployedBot(Base):
    __tablename__ = 'deployed_bots'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    botusername = Column(String)
    botpassword = Column(String)
    flowise_link = Column(String)



DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

@app.post('/deploy_bot')
async def deploy_bot(item: Item):
    print(item)
    if(register_bot(item.botusername,item.botpassword,item.botdisplayname)):
        bot = DeployedBot(username=item.username, botusername=item.botusername, botpassword=item.botpassword, flowise_link=item.flowise_link)
        session.add(bot)
        session.commit()

        # Define environment variables for the bot container
        env = {
            'USER_ID': item.botusername,
            'PASSWORD': item.botpassword,
            'BOT_OWNER': item.username,
            'DEVICE_ID': 'chatgptbot',
            'FLOWISE_API_URL': item.flowise_link,
            'HOMESERVER': "https://matrix.immagine.ai"
        }

        # Run the bot container
        container = client.containers.run(
            'agifm/matrix_chatgpt_bot',  # Replace with the actual image name
            detach=True,
            environment=env
        )

        return {'message': 'Bot deployed successfully'}

@app.get('/get_bots')
async def get_bots(username: str = Query(...)):
    # username = username.replace('immagine.ai','agi.fm')
    bots = session.query(DeployedBot).filter(DeployedBot.username == username).all()
    return [f"@{i.botusername}:immagine.ai" for i in bots]

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

