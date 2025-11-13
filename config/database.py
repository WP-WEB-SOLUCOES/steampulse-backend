from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import certifi

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# --- Nomes das Coleções ---
DB_NAME = "vertexplay"
GAMES_COLLECTION = "games"
DLCS_COLLECTION = "dlcs"
MUSIC_COLLECTION = "music"
DEMOS_COLLECTION = "demos"
USERS_COLLECTION = "users"

# --- Conexão ---
try:
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]

    # Disponibiliza as coleções para serem importadas
    games_collection = db[GAMES_COLLECTION]
    dlcs_collection = db[DLCS_COLLECTION]
    music_collection = db[MUSIC_COLLECTION]
    demos_collection = db[DEMOS_COLLECTION]
    user_collection = db[USERS_COLLECTION]
    
    print("Conexão com o MongoDB e coleções estabelecida com sucesso!")

except Exception as e:
    print(f"Erro ao conectar com o MongoDB: {e}")
    exit()


# --- FUNÇÃO AUXILIAR QUE ESTAVA FALTANDO ---
def user_helper(user_data) -> dict:
    """
    Converte um documento de usuário do MongoDB para um dicionário Python,
    convertendo o _id para uma string.
    """
    return {
        "id": str(user_data["_id"]),
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "games": user_data.get("games", []),
        "admin": user_data.get("admin", False),
        "vauncher": user_data.get("vauncher", 0),
        "invite_code": user_data.get("invite_code", ""),
    }