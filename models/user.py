from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class UserAuthSchema(BaseModel):
    """
    Schema para receber os dados de registro/autenticação do usuário.
    """
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "fuyuki kuro",
                "email": "fuyuki@app.com",
                "password": "senha_forte_123"
            }
        }

class UserInDB(BaseModel):
    """
    Schema que representa o documento completo do usuário no banco de dados MongoDB.
    """
    name: str
    email: EmailStr
    password: str  # Armazena a senha já "hasheada" (criptografada)
    games: List[dict] = Field(default_factory=list)
    admin: bool = False
    vauncher: int = 0
    invite_code: str = ""

class TokenData(BaseModel):
    """
    Schema para os dados contidos dentro do token JWT.
    """
    email: Optional[EmailStr] = None