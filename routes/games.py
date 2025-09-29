# routes/games.py
from fastapi import APIRouter, Body, HTTPException, Depends
from config.database import user_collection
from models.game import AddGameSchema
from .auth import get_current_user

router = APIRouter()

@router.post("/add-to-library", tags=["Jogos e Biblioteca"])
async def add_game_to_library(
    game: AddGameSchema = Body(...), 
    current_user: dict = Depends(get_current_user)
):
    """Adiciona um jogo à biblioteca do usuário logado."""
    user_email = current_user["email"]
    
    result = await user_collection.update_one(
        {"email": user_email},
        {"$addToSet": {"games": game.steam_appid}}
    )

    if result.modified_count == 0 and result.matched_count > 0:
        return {"message": "Este jogo já está na sua biblioteca."}
        
    if result.modified_count > 0:
        return {"message": "Jogo adicionado à sua biblioteca com sucesso!"}

    raise HTTPException(status_code=404, detail="Usuário não encontrado")