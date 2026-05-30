import os
import jwt
import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_ISSUER = os.getenv("JWT_ISSUER", "https://sistema-distribuido-trabalho-faculd.vercel.app")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "internal-apis")
JWT_PUBLIC_KEY_PEM = os.getenv("JWT_PUBLIC_KEY_PEM", "").replace("\\n", "\n")

security = HTTPBearer()

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_PUBLIC_KEY_PEM,
            algorithms=["RS256"],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE
        )
        
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token claims")
            
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")

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
        
    except requests.exceptions.RequestException:
        return []

def get_local_console_top_8(platform_name: str):
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

@app.get("/compare")
def get_compare(user_id: str = Depends(verificar_token)):
    steam_data = get_cheapshark_top_8()
    epic_mock = [{"platform": "Epic", "name": "GTA V", "score": "96", "image": "epic_gta.jpg"}]
    
    ps_data = get_local_console_top_8("PlayStation")
    xbox_data = get_local_console_top_8("Xbox")
    
    comparison = []
    
    if steam_data: 
        comparison.append(steam_data[0])
    if epic_mock: 
        comparison.append(epic_mock[0])
    if ps_data: 
        comparison.append(ps_data[0])
    if xbox_data: 
        comparison.append(xbox_data[0])

    comparison_sorted = sorted(comparison, key=lambda x: int(x.get('score', 0)), reverse=True)
    
    return {
        "success": True,
        "authenticated_user_id": user_id, 
        "data": comparison_sorted
    }

@app.get("/")
def home():
    return {"status": "Microsserviço de Ranking GameVerse está rodando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
