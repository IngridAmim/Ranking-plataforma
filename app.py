import os
import jwt
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
            raise HTTPException(status_code=401, detail="Acesso negado")
            
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessão expirada")
    except Exception:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")

def get_banco_de_dados_jogos():
    return [
        # PLAYSTATION
        {"platform": "PlayStation", "name": "God of War Ragnarök", "score": "94", "image": "https://cdn.akamai.steamstatic.com/steam/apps/2322010/header.jpg"},
        {"platform": "PlayStation", "name": "The Last of Us Part II", "score": "93", "image": "https://image.api.playstation.com/vulcan/ap/rnd/202008/1020/T45iRN1bhiWcJUzWN6ubTEcb.png"},
        {"platform": "PlayStation", "name": "Spider-Man 2", "score": "90", "image": "https://image.api.playstation.com/vulcan/ap/rnd/202306/1219/1c7b75d8ed9271516546560d219ad0b22ee0a263b4537bd8.png"},
        {"platform": "PlayStation", "name": "Horizon Forbidden West", "score": "88", "image": "https://cdn.akamai.steamstatic.com/steam/apps/2420110/header.jpg"},
        {"platform": "PlayStation", "name": "Ghost of Tsushima", "score": "87", "image": "https://cdn.akamai.steamstatic.com/steam/apps/2215430/header.jpg"},
        {"platform": "PlayStation", "name": "Demon's Souls", "score": "92", "image": "https://image.api.playstation.com/vulcan/img/rnd/202011/1717/BXrwEBVEBofwKkGAqNn6LUNV.png"},
        {"platform": "PlayStation", "name": "Bloodborne", "score": "92", "image": "https://image.api.playstation.com/vulcan/img/rnd/202010/2614/FmXEBhaP2LxEsG2m1lTIfaOa.png"},
        {"platform": "PlayStation", "name": "Ratchet & Clank: Rift Apart", "score": "88", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1895880/header.jpg"},
        
        # XBOX
        {"platform": "Xbox", "name": "Halo Infinite", "score": "87", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1240440/header.jpg"},
        {"platform": "Xbox", "name": "Forza Horizon 5", "score": "92", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1551360/header.jpg"},
        {"platform": "Xbox", "name": "Starfield", "score": "83", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1716740/header.jpg"},
        {"platform": "Xbox", "name": "Gears 5", "score": "84", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1097840/header.jpg"},
        {"platform": "Xbox", "name": "Sea of Thieves", "score": "81", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1172620/header.jpg"},
        {"platform": "Xbox", "name": "Microsoft Flight Simulator", "score": "91", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1250410/header.jpg"},
        {"platform": "Xbox", "name": "Hi-Fi RUSH", "score": "89", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1817230/header.jpg"},
        {"platform": "Xbox", "name": "Ori and the Will of the Wisps", "score": "90", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1057090/header.jpg"},

        # STEAM (PC)
        {"platform": "Steam", "name": "Cyberpunk 2077", "score": "86", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg"},
        {"platform": "Steam", "name": "Elden Ring", "score": "96", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1245620/header.jpg"},
        {"platform": "Steam", "name": "Baldur's Gate 3", "score": "96", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1086940/header.jpg"},
        {"platform": "Steam", "name": "Hollow Knight", "score": "90", "image": "https://cdn.akamai.steamstatic.com/steam/apps/367520/header.jpg"},
        {"platform": "Steam", "name": "Stardew Valley", "score": "89", "image": "https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg"},
        {"platform": "Steam", "name": "Red Dead Redemption 2", "score": "93", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1174180/header.jpg"},
        {"platform": "Steam", "name": "Helldivers 2", "score": "82", "image": "https://cdn.akamai.steamstatic.com/steam/apps/553850/header.jpg"},
        {"platform": "Steam", "name": "Lethal Company", "score": "85", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1966720/header.jpg"},

        # EPIC GAMES
        {"platform": "Epic", "name": "Fortnite", "score": "81", "image": "https://cdn2.unrealengine.com/blade-2560x1440-2560x1440-d4e556fb8166.jpg"},
        {"platform": "Epic", "name": "Alan Wake 2", "score": "89", "image": "https://cdn2.unrealengine.com/egs-alanwake2-remedyentertainment-g1a-00-1920x1080-6058e5d0bfcb.jpg"},
        {"platform": "Epic", "name": "Rocket League", "score": "86", "image": "https://cdn2.unrealengine.com/egs-rocketleague-psyonixllc-g1a-00-1920x1080-b7dc444fb408.jpg"},
        {"platform": "Epic", "name": "Genshin Impact", "score": "81", "image": "https://cdn2.unrealengine.com/egs-genshinimpact-mihoyolimited-g1a-00-1920x1080-0a259c7b9db1.jpg"},
        {"platform": "Epic", "name": "Fall Guys", "score": "81", "image": "https://cdn2.unrealengine.com/egs-fallguys-mediatonic-g1a-00-1920x1080-2a558dc06d91.jpg"},
        {"platform": "Epic", "name": "Valorant", "score": "80", "image": "https://cdn2.unrealengine.com/egs-valorant-riotgames-g1a-00-1920x1080-b8f9e68ba9b0.jpg"},
        {"platform": "Epic", "name": "Dead Island 2", "score": "73", "image": "https://cdn2.unrealengine.com/egs-deadisland2-dambusterstudios-g1a-00-1920x1080-1a7eecc10e05.jpg"},
        {"platform": "Epic", "name": "Hades", "score": "93", "image": "https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg"}
    ]

@app.get("/compare")
def get_compare(user_id: str = Depends(verificar_token)):
    todos_os_jogos = get_banco_de_dados_jogos()
    jogos_ordenados = sorted(todos_os_jogos, key=lambda x: int(x.get('score', 0)), reverse=True)
    
    for index, jogo in enumerate(jogos_ordenados):
        jogo["rank"] = index + 1
    
    return {"data": jogos_ordenados}

@app.get("/")
def home():
    return {"status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
