# config/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis do .env

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
database = client.get_database("vertex_play_db") # Escolha um nome para o seu banco

# Coleção de usuários
user_collection = database.get_collection("users")

# Helper para converter o _id do MongoDB
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "games": user.get("games", [])
    }