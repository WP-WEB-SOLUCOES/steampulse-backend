from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

from config.database import user_collection, user_helper
from models.user import UserAuthSchema, TokenData, UserInDB

# --- Configurações de Segurança ---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "uma_chave_secreta_padrao_para_desenvolvimento")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30 # Token expira em 30 dias

# Contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de segurança para a documentação do Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticação"]
)

# --- Funções Auxiliares de Segurança ---

def verify_password(plain_password, hashed_password):
    """Verifica se a senha fornecida corresponde ao hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependência de Autenticação ---

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Decodifica o token JWT para obter o usuário atual.
    Esta função é usada como uma dependência em rotas protegidas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await user_collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user_helper(user)

# --- Rotas (Endpoints) ---

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def create_user(user_data: UserAuthSchema):
    """Registra um novo usuário no banco de dados com senha criptografada."""
    existing_user = await user_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário com este email já existe")

    # CRIPTOGRAFA A SENHA ANTES DE SALVAR
    hashed_password = get_password_hash(user_data.password)
    
    new_user = UserInDB(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password, # Salva a senha criptografada
        games=[], admin=False, vauncher=0, invite_code="" 
    )
    await user_collection.insert_one(new_user.model_dump())
    return {"message": "Usuário criado com sucesso!"}

# --- GARANTA QUE ESTA ROTA EXISTA E ESTEJA CORRETA ---
@router.post("/login", summary="Login for access token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await user_collection.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", summary="Get current user profile")
async def read_users_me(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Retorna os dados do usuário atualmente autenticado."""
    return current_user