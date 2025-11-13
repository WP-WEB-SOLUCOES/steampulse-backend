# security/auth_handler.py
import time
import jwt  # Agora estamos usando a biblioteca PyJWT
from typing import Dict
import os
import bcrypt
from datetime import datetime, timedelta, timezone # Novo import para a data de expiração
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

# --- Funções de Senha (usando bcrypt) - NÃO MUDAM ---
def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


# --- Funções de JWT (REESCRITAS COM PyJWT) ---

def sign_jwt(user_email: str) -> Dict[str, str]:
    """Gera e assina um novo Access Token usando PyJWT."""
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1), # Expira em 1 hora a partir de agora
        'iat': datetime.now(timezone.utc), # Data de emissão
        'sub': user_email, # 'subject', o padrão para identificar o usuário
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token}


def decode_jwt(token: str) -> dict:
    """Decodifica um token. PyJWT lida com a expiração automaticamente."""
    try:
        # A própria função decode já verifica a assinatura e a expiração
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("!!! ERRO DE JWT: Token expirado.")
        return {}
    except jwt.InvalidTokenError as e:
        # Captura outros erros de token (assinatura inválida, malformado, etc.)
        print(f"!!! ERRO DE JWT: Token inválido - {e}")
        return {}