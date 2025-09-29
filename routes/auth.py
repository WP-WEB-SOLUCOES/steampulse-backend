# routes/auth.py
from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.database import user_collection, user_helper
from models.user import UserSchema, UserLoginSchema
from security.auth_handler import sign_jwt, decode_jwt, get_password_hash, verify_password

router = APIRouter()
security = HTTPBearer()

# Dependência para proteger rotas
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Token inválido ou expirado")
    
    user_email = payload.get("user_email")
    user = await user_collection.find_one({"email": user_email})
    if user is None:
        raise HTTPException(status_code=403, detail="Usuário não encontrado")
    return user_helper(user)


@router.post("/register", tags=["Autenticação"])
async def create_user(user: UserSchema = Body(...)):
    # Verifica se o email já existe
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário com este email já existe")

    # Criptografa a senha
    user.password = get_password_hash(user.password)
    new_user = await user_collection.insert_one(user.model_dump())
    return {"message": "Usuário criado com sucesso!"}


@router.post("/login", tags=["Autenticação"])
async def user_login(user: UserLoginSchema = Body(...)):
    db_user = await user_collection.find_one({"email": user.email})
    if db_user and verify_password(user.password, db_user["password"]):
        return sign_jwt(user.email)
    
    raise HTTPException(status_code=401, detail="Email ou senha incorretos")


@router.get("/profile", tags=["Usuário"], dependencies=[Depends(get_current_user)])
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}