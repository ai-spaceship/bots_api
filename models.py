from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class Item(BaseModel):
    email_id: Optional[str]
    bot_username: str
    api_key: str
    agent_name: str
    agent_desc: str
    agent_id: str
    profile: str
    tags: str
    publish: bool

class WorkflowItem(BaseModel):
    email_id: Optional[str]
    bot_username: str
    api_key: str
    workflow_name: str
    workflow_desc: str
    workflow_id: str
    profile: Optional[str]
    tags: str
    publish: bool


class Users(BaseModel):
    email_id: str
    bot_username: str
    name: str

class UserCreate(BaseModel):
    username: str

class AgentUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str] = Field(alias="desc")
    avatar: Optional[str] = Field("avatar_mxc")

class Bots(BaseModel):
    id: str
    username: str
    bot_username: str
    desc: str
    name: str
    tags: list
    type: str
    avatar_mxc: Optional[str]
    profile_photo: Optional[str]

class Agent(BaseModel):
    username: str
    email_id: Optional[str]
    agent_id: str

class MergedList(BaseModel):
    personal: list[Bots]
    public: list[Bots]




    

