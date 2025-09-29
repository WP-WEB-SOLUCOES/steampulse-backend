# models/game.py
from pydantic import BaseModel, Field

class AddGameSchema(BaseModel):
    steam_appid: int = Field(...)

    class Config:
        json_schema_extra = { "example": { "steam_appid": 730 } }