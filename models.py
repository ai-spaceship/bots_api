from pydantic import BaseModel

class Item(BaseModel):
    email_id: str
    bot_username: str
    api_key: str
    agent_name: str
    agent_desc: str
    agent_id: str
    profile: str


class Users(BaseModel):
    email_id: str
    bot_username: str
    agent_name: str


class UserCreate(BaseModel):
    username: str

    

