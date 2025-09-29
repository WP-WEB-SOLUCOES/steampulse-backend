# main.py
from fastapi import FastAPI
from routes.auth import router as AuthRouter
from routes.games import router as GamesRouter
from routes.payments import router as PaymentsRouter

# --- CONFIGURAÇÃO ATUALIZADA PARA O BOTÃO "AUTHORIZE" ---
# Trocamos o tipo para 'apiKey' para ter mais controle sobre a UI da documentação.
# A forma como a API funciona continua a mesma (HTTP Bearer Token).
security_schemes = {
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "apiKey", # MUDANÇA: de 'http' para 'apiKey'
                "in": "header",   # Onde a chave será enviada (no cabeçalho)
                "name": "Authorization", # O NOME DO CAMPO que aparecerá no popup
                "description": "Cole seu token JWT aqui, precedido pela palavra 'Bearer ' (ex: Bearer eyJ...)"
            }
        }
    },
    # Esta parte garante que o cadeado apareça nas rotas
    "security": [{"BearerAuth": []}], 
}
# ---------------------------------------------------------

app = FastAPI(
    title="Vertex Play API",
    description="API para a plataforma de jogos Vertex Play.",
    version="1.0.0",
    # Usamos o openapi_extra para injetar nossa configuração customizada
    openapi_extra=security_schemes
)

# O restante do arquivo continua igual...
app.include_router(AuthRouter, prefix="/api/auth", tags=["Autenticação"])
app.include_router(GamesRouter, prefix="/api/games", tags=["Jogos e Biblioteca"])
app.include_router(PaymentsRouter, prefix="/api/payments", tags=["Pagamentos"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API do Vertex Play!"}