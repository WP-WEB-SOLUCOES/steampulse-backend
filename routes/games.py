from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional, Annotated, Any, Dict
from bson import ObjectId
import asyncio

# Importa as coleções e helpers necessários
from config.database import user_collection, games_collection, dlcs_collection, music_collection, demos_collection
from models.games import GameSchema, PaginatedGamesResponse
from routes.auth import get_current_user

router = APIRouter(
    prefix="/api/games",
    tags=["Games"]
)

# Função auxiliar para converter _id para string em uma lista de documentos
def serialize_results(results: list) -> list:
    for item in results:
        if '_id' in item and isinstance(item['_id'], ObjectId):
            item['_id'] = str(item['_id'])
    return results

@router.get("/", response_model=PaginatedGamesResponse, summary="Get All Games With Pagination")
async def get_all_games_with_pagination(
    last_id: Optional[str] = Query(None, alias="last_id", description="ID do último item da página anterior para paginação"),
    page_size: int = Query(20, ge=1, le=100, description="Número de itens por página"),
    direction: str = Query("next", pattern="^(next|prev)$", description="Direção da paginação ('next' ou 'prev')"),
    type: str = Query("games", pattern="^(games|dlcs|music|demos)$", description="Tipo de conteúdo a ser buscado")
):
    """
    Retorna uma lista paginada de itens (jogos, DLCs, etc.)
    baseado no tipo solicitado.
    """
    
    collection_map = {
        "games": games_collection,
        "dlcs": dlcs_collection,
        "music": music_collection,
        "demos": demos_collection,
    }
    collection = collection_map[type]

    query = {}
    if last_id:
        try:
            object_id = ObjectId(last_id)
            if direction == "next":
                query["_id"] = {"$gt": object_id}
            else: # prev
                query["_id"] = {"$lt": object_id}
        except Exception:
            raise HTTPException(status_code=400, detail="last_id inválido")

    sort_order = 1 if direction == "next" else -1

    cursor = collection.find(query).sort("_id", sort_order).limit(page_size)
    results = await cursor.to_list(length=page_size)

    if direction == "prev":
        results.reverse()

    # --- CORREÇÃO PRINCIPAL AQUI ---
    # Os cursores devem ser calculados ANTES da serialização final para o Pydantic,
    # mas a chave a ser lida do dicionário do MongoDB é '_id'.
    next_cursor = str(results[-1]['_id']) if results else None
    prev_cursor = str(results[0]['_id']) if results else None
    
    # Serializa os resultados para a resposta (converte ObjectId para str)
    serialized_data = serialize_results(results)

    return {
        "next_cursor": next_cursor,
        "prev_cursor": prev_cursor,
        "results": serialized_data
    }

@router.get("/search", response_model=List[GameSchema], summary="Search Games")
async def search_games(name: str = Query(..., min_length=2, description="Nome do jogo a ser procurado")):
    """
    Busca por um nome de jogo em todas as coleções.
    """
    query = {"nome": {"$regex": name, "$options": "i"}}
    
    tasks = [
        games_collection.find(query).to_list(length=10),
        dlcs_collection.find(query).to_list(length=10),
        music_collection.find(query).to_list(length=5),
        demos_collection.find(query).to_list(length=5),
    ]

    results_from_collections = await asyncio.gather(*tasks)

    combined_results = []
    for result_list in results_from_collections:
        combined_results.extend(result_list)
        
    unique_results = {item['steam_appid']: item for item in combined_results}.values()

    return serialize_results(list(unique_results))

@router.post("/add-game-to-user", status_code=status.HTTP_200_OK, summary="Add Game To User Library")
async def add_game_to_user_library(
    game: GameSchema, 
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Adiciona um jogo à lista de jogos do usuário autenticado.
    """
    try:
        user_email = current_user["email"]
        game_dict = game.model_dump(by_alias=True)
        if 'id' in game_dict:
            del game_dict['id']
        
        result = await user_collection.update_one(
            {"email": user_email},
            {"$addToSet": {"games": game_dict}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {"status": "success", "message": f"Jogo '{game.nome}' adicionado à biblioteca."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))