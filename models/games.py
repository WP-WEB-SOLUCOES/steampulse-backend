from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class GameSchema(BaseModel):
    id: str = Field(..., alias="_id")
    steam_appid: int
    nome: str
    tipo: str
    descricao_curta: str
    imagem_cabecalho: str
    generos: List[str]
    data_lancamento: str
    gratuito: bool
    link_manifesto: str
    verify: bool
    working: bool
    installdir: Optional[str] = None
    
    # Campos que ainda existem nos dados, mas que agora são opcionais no schema
    # para evitar erros se não existirem
    screenshots: Optional[List[str]] = []
    plataformas: Optional[Dict[str, bool]] = {}
    desenvolvedores: Optional[List[str]] = []
    publicadoras: Optional[List[str]] = []
    preco_final: Optional[float] = 0.0
    preco_original: Optional[float] = 0.0
    desconto_percentual: Optional[int] = 0

    # Campos 'is_lancamento' e 'is_popular' foram REMOVIDOS

    class Config:
        populate_by_name = True
        json_encoders = { "ObjectId": str }

class PaginatedGamesResponse(BaseModel):
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    results: List[GameSchema]