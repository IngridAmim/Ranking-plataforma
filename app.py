from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import jwt # Biblioteca instalada via 'pip install PyJWT'

app = FastAPI()

# Permite que o Front-end deles consuma a nossa API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INÍCIO DO SISTEMA DE SEGURANÇA (MIDDLEWARE EXIGIDO NO VÍDEO/PDF) ---

security = HTTPBearer()

# --- VALORES REAIS EXTRAÍDOS DO PDF (guia_validar_jwt.pdf) ---
SECRET_KEY = "super-secret-key-that-everyone-knows" # Chave JWT_SECRET do PDF
ALGORITHM = "HS256"
EXPECTED_ISSUER = "auth_service"   # Valor da chave JWT_ISSUER no PDF
EXPECTED_AUDIENCE = "gameverse_api" # Valor da chave JWT_AUDIENCE no PDF

# Esta função age como o "Segurança da Porta" da sua API
def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Tenta ler e VALIDAR o crachá conforme as regras do PDF e do Vídeo
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=EXPECTED_ISSUER,   # Valida o emissor (iss) -auth_service-
            audience=EXPECTED_AUDIENCE # Valida o receptor (aud) -gameverse_api-
        )
        
        # Extrai o ID do usuário (o payload.sub exigido pelo colega no vídeo!)
        user_id: str = payload.get("sub") 
        
        if user_id is None:
            # Erro 401: O ID do usuário não veio no token
            raise HTTPException(status_code=401, detail="Token inválido. Faltando o ID do usuário (sub).")
            
        return user_id # Se der tudo certo, ele deixa passar e entrega o ID
        
    except jwt.ExpiredSignatureError:
        # Erro 401: O token já passou da validade
        raise HTTPException(status_code=401, detail="Token expirado. Refaça o login.")
    except jwt.InvalidIssuerError:
        # Erro 401: O token não foi emitido pelo auth_service
        raise HTTPException(status_code=401, detail="Emissor do token inválido (iss).")
    except jwt.InvalidAudienceError:
        # Erro 401: O token não é para a gameverse_api
        raise HTTPException(status_code=401, detail="Receptor do token inválido (aud).")
    except jwt.InvalidTokenError as e:
        # Erro 401: Qualquer outro erro genérico de token falso
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

# --- FIM DO SISTEMA DE SEGURANÇA ---


# --- LÓGICA DE JOGOS (MANTIDA DO SEU TRABALHO ANTERIOR) ---

# Função para buscar Top 8 da Steam via CheapShark (Dados Reais)
def get_cheapshark_top_8():
    cheapshark_url = "https://www.cheapshark.com/api/1.0/deals?storeID=1&lowerPrice=0&limit=8&onSale=1&sortBy=metacritic"
    try:
        response = requests.get(cheapshark_url)
        response.raise_for_status()
        deals = response.json()
        
        ranking_formatado = []
        for index, deal in enumerate(deals):
            if deal.get("metacriticScore") and deal.get("metacriticScore") != "0":
                game_data = {
                    "rank": index + 1,
                    "platform": "Steam",
                    "name": deal.get("title"),
                    "image": deal.get("thumb"),
                    "score": deal.get("metacriticScore")
                }
                ranking_formatado.append(game_data)
        
        return ranking_formatado[:8]
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar a CheapShark API: {e}")
        return [] # Retorna array vazio em caso de falha (Tolerância a Falhas)

# Nó Local Simulado para PlayStation/Xbox (Fallback Strategy)
def get_local_console_top_8(platform_name: str):
    # Mock data simulando um banco de dados interno
    mock_data = [
        {"name": "God of War Ragnarök", "score": "94"},
        {"name": "Spider-Man 2", "score": "90"},
        {"name": "The Last of Us Part I", "score": "88"}
    ]
    
    ranking_formatado = []
    for index, game in enumerate(mock_data):
        game_data = {
            "rank": index + 1,
            "platform": platform_name,
            "name": game.get("name"),
            "image": f"https://example.com/mock_images/{platform_name}.jpg",
            "score": game.get("score")
        }
        ranking_formatado.append(game_data)
        
    return ranking_formatado[:8]


# --- ROTAS DA API (SISTEMA DISTRIBUÍDO E FUSÃO DE DADOS) ---

# Rota /compare: REALIZA A FUSÃO DE DADOS (DATA FUSION) DE MÚLTIPLOS NÓS
# ATENÇÃO: Esta rota agora está PROTEGIDA pelo middleware Depends(verificar_token)
@app.get("/compare")
def get_compare(user_id: str = Depends(verificar_token)):  # <-- PROTEÇÃO JWT AQUI
    """
    Rota Inteligente: Busca os líderes de 4 nós distribuídos e faz a fusão ordenada.
    """
    
    # Opcional: Se você quiser ver o ID do usuário autenticado no terminal de produção
    print(f"A requisição /compare foi feita pelo usuário autenticado: {user_id}")
    
    # 1. Coleta os dados de nós Externos (PC)
    steam_data = get_cheapshark_top_8() # Bate na API real CheapShark
    # Mock para Epic (poderia ser outra API real)
    epic_mock = [{"platform": "Epic", "name": "GTA V", "score": "96", "image": "epic_gta.jpg"}]
    
    # 2. Coleta os dados de nós Locais/Cache (Consoles)
    ps_data = get_local_console_top_8("PlayStation") # Simula DB local
    xbox_data = get_local_console_top_8("Xbox")     # Simula DB local
    
    comparison = []
    
    # Captura apenas o Top 1 de cada nó distribuído para comparação rápida (Data Fusion)
    if steam_data: 
        comparison.append(steam_data[0]) # Líder Steam
    if epic_mock: 
        comparison.append(epic_mock[0])   # Líder Epic
    if ps_data: 
        comparison.append(ps_data[0])     # Líder PSN
    if xbox_data: 
        comparison.append(xbox_data[0])   # Líder Xbox

    # Ordena os líderes pelo Metascore (do maior para o menor)
    comparison_sorted = sorted(comparison, key=lambda x: int(x.get('score', 0)), reverse=True)
    
    # Adiciona a informação de ID do usuário que fez a requisição na resposta
    # (Bom para o Guilherme ver que funcionou!)
    return {
        "success": True,
        "authenticated_user_id": user_id, 
        "data": comparison_sorted
    }

# Rota genérica para testar se a API está viva (Não precisa de proteção)
@app.get("/")
def home():
    return {"status": "Microsserviço de Ranking GameVerse está rodando!"}

# --- FIM DO MOTOR DO MICROSSERVIÇO ---

if __name__ == "__main__":
    import uvicorn
    # Liga o servidor Uvicorn na porta 8000
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)