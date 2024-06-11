from typing import Optional
from pydantic import BaseModel, Field


class Item(BaseModel):
    email_id: Optional[str]
    bot_username: str
    api_key: str
    name: str
    description: str
    id: str
    profile: Optional[str]
    tags: str
    publish: bool
    type: str
    streaming: Optional[bool] = Field(default=False)
    publish_all : bool
    category: Optional[str]

class BotList(BaseModel):
    bots : list


class AgentUpdate(BaseModel):
    name: Optional[str]
    desc: Optional[str] = Field(alias="description")
    avatar_mxc: Optional[str] = Field(alias="avatar")
    prompt: Optional[str]
    llmModel: Optional[str]


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
    prompt: Optional[str]
    llmModel: Optional[str]


class Duplicate(BaseModel):
    username: str
    agent_id: str
    owner_id: Optional[str]
    name:     str
    description:  str
