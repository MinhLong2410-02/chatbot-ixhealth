from pydantic import BaseModel
from typing import List
class UserLogin(BaseModel):
    user_id: int
    password: str
    
class UserCreate(BaseModel):
    username: str
    image: str
    token: str

class ChannelCreate(BaseModel):
    user_ids: List[int]
    coach_id: int

class BotQuery(BaseModel):
    query_text: str
    
class BotResponse(BaseModel):
    response: str