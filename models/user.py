# models/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import List

class UserSchema(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    games: List[int] = Field(default_factory=list)

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)