# security/auth_handler.py
import time
from typing import Dict
from jose import jwt # <-- ESTA É A LINHA MAIS IMPORTANTE E A CAUSA DO ERRO
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

# --- FUNÇÕES DE SENHA (usando bcrypt) ---

def get_password_hash(password: str) -> str:
    """Criptografa a senha em texto plano."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde à senha criptografada."""
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


# --- FUNÇÕES DE JWT (usando python-jose) ---

def sign_jwt(user_email: str) -> Dict[str, str]:
    payload = {
        "user_email": user_email,
        "expires": time.time() + 3600 # Token expira em 1 hora
    }
    # Agora o 'jwt' aqui é garantido que seja da biblioteca 'jose'
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token}


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}