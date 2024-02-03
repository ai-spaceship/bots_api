from typing import Optional
from pydantic import BaseModel, Op

class Item(BaseModel):
    email_id: Optional[str]
    bot_username: str
    api_key: str
    agent_name: str
    agent_desc: str
    agent_id: str
    profile: str

class WorkflowItem(BaseModel):
    email_id: Optional[str]
    bot_username: str
    api_key: str
    workflow_name: str
    workflow_desc: str
    workflow_id: str
    profile: Optional[str]


class Users(BaseModel):
    email_id: str
    bot_username: str
    agent_name: str


class UserCreate(BaseModel):
    username: str

class AgentUpdate(BaseModel):
    isActive: Optional[bool]
    name: Optional[str]
    initialMessage: Optional[str]
    prompt: Optional[str]
    llmModel: Optional[str]
    description: Optional[str]
    avatar: Optional[str]

    

