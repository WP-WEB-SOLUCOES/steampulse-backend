# models/payment.py
from pydantic import BaseModel, Field

class PaymentSchema(BaseModel):
    game_id: int = Field(...)
    amount: float = Field(...)
    description: str = Field(...)

    class Config:
        json_schema_extra = { 
            "example": { 
                "game_id": 730, 
                "amount": 49.99,
                "description": "Compra do jogo Counter-Strike 2"
            } 
        }