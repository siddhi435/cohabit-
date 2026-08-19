import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
load_dotenv()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict

app = FastAPI()

# Session middleware for OAuth
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# OAuth client setup (supports GitHub and Google)
oauth = OAuth()
oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID", ""),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

# Simple file-backed session storage
SESSIONS_PATH = os.path.join("data", "sessions.json")

def load_sessions() -> Dict[str, dict]:
    if not os.path.exists(SESSIONS_PATH):
        return {}
    try:
        with open(SESSIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_sessions(sessions: Dict[str, dict]):
    os.makedirs(os.path.dirname(SESSIONS_PATH), exist_ok=True)
    with open(SESSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)

def create_persistent_session(user_obj: dict) -> str:
    sessions = load_sessions()
    sid = str(uuid4())
    sessions[sid] = {"user": user_obj}
    save_sessions(sessions)
    return sid

def delete_persistent_session(sid: str):
    sessions = load_sessions()
    if sid in sessions:
        del sessions[sid]
        save_sessions(sessions)

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "openid email profile"},
)

# ----------------- CORS MIDDLEWARE -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all websites to connect (crucial for local testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------------------------------------------

# Track active WebSocket connections from browsers
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# Clear, explicit WebSocket Route (Supports both slash configurations)
@app.websocket("/ws/notifications")
@app.websocket("/ws/notifications/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Trigger API Endpoint
@app.post("/api/trigger-match")
async def trigger_match():
    await manager.broadcast({
        "type": "NEW_MATCH", 
        "message": "A new compatible roommate match has been found!"
    })
    return {"status": "success"}

# Mount static files to an internal path so it doesn't fight over "/"
app.mount("/static", StaticFiles(directory="web"), name="static")

# 🆕 ENDPOINT 1: Fetch dashboard box counts from user.json
@app.get("/api/dashboard-metrics")
async def get_dashboard_metrics():
    json_path = os.path.join("data", "user.json")
    
    # Safely load JSON data or fall back to zeros if empty/missing
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                user_data = {}
    else:
        user_data = {}

    # Extract metrics or count arrays dynamically
    return {
        "matches_count": user_data.get("matches_count", 0),
        "liked_count": len(user_data.get("liked_profiles", [])),
        "saved_count": len(user_data.get("saved_profiles", [])),
        "average_compatibility": user_data.get("average_compatibility", "0%")
    }

# 🆕 ENDPOINT 2: Serve roommate lists from your CSV file
@app.get("/api/recommendations")
async def get_recommendations():
    """Return a small list of recommendations from CSV. This endpoint is robust when pandas is not installed
    or when the expected CSV filename differs (looks for the -1 variant as well)."""
    try:
        import pandas as pd
    except Exception:
        # pandas not available; return an empty recommendations list instead of raising a 500
        return {"recommendations": [], "count": 0}

    # Try both possible filenames that may exist in the data/ folder
    candidates = ["Girls_pg_hostel_CSV_data.csv", "Girls_pg_hostel_CSV_data-1.csv"]
    csv_path = None
    for name in candidates:
        candidate_path = os.path.join("data", name)
        if os.path.exists(candidate_path):
            csv_path = candidate_path
            break

    if not csv_path:
        return {"recommendations": [], "count": 0}

    try:
        df = pd.read_csv(csv_path)
        records = df.head(5).to_dict(orient="records")
        return {"recommendations": records, "count": len(df)}
    except Exception:
        return {"recommendations": [], "count": 0}


# 🆕 ENDPOINT 3: Data schema and profile capture for test_post.py
@app.post("/api/custom-matches")
async def save_custom_profile(request: Request):
    json_path = os.path.join("data", "user.json")
    os.makedirs("data", exist_ok=True)
    
    # Accept flexible JSON payloads from the frontend form (no strict pydantic validation)
    try:
        profile_dict = await request.json()
    except Exception:
        profile_dict = {}
    
    # Persist a copy for the dashboard and later retrieval
    profile_dict["matches_count"] = 12       
    profile_dict["liked_profiles"] = []      
    profile_dict["saved_profiles"] = []      
    profile_dict["average_compatibility"] = "88%"
    
    with open(json_path, "w") as f:
        json.dump(profile_dict, f, indent=4)

    # Build a UserProfile object compatible with RecommendationEngine using src.models
    try:
        from src.main import load_users
        from src.recommender import RecommendationEngine
        from src.interactions import get_user_interactions
        from src.models import UserProfile as UserProfileModel
    except Exception:
        # Fallback: return the simple acknowledgement so older clients don't break
        await manager.broadcast({
            "type": "NEW_MATCH", 
            "message": f"Custom profile updated for {profile_dict.get('name', 'user')}!"
        })
        return {"status": "success", "message": "Profile received!"}

    # Construct a UserProfileModel instance for matching
    # Map incoming dict values to the internal UserProfileModel, using safe defaults
    custom_user = UserProfileModel(
        id=0,
        name=profile_dict.get("name", "Guest"),
        gender=profile_dict.get("gender", "Any"),
        preferred_gender=profile_dict.get("preferred_gender", "Any"),
        cleanliness=profile_dict.get("cleanliness", "Moderate"),
        sleep_schedule=profile_dict.get("sleep_type", profile_dict.get("sleep_schedule", "")),
        guests=str(profile_dict.get("social_energy_rating", profile_dict.get("guests", "3"))),
        smoking=(profile_dict.get("smoking_drinking") == "Smoker"),
        bio=profile_dict.get("bio", ""),
        work_shift=profile_dict.get("work_shift", ""),
        profession=profile_dict.get("profession", ""),
        personality=profile_dict.get("personality", "Balanced"),
        bedtime=profile_dict.get("bedtime", ""),
        wake_time=profile_dict.get("wake_time", ""),
        sleep_type=profile_dict.get("sleep_type", ""),
        noise_preference=profile_dict.get("noise_preference", ""),
        social_energy_rating=int(profile_dict.get("social_energy_rating", profile_dict.get("guests", 3))) if str(profile_dict.get("social_energy_rating", profile_dict.get("guests", 3))).isdigit() else 3,
        room_type_preference=profile_dict.get("room_type_preference", ""),
        privacy_importance=profile_dict.get("privacy_importance", "Medium"),
        pets=profile_dict.get("pets", "No Pets"),
        smoking_drinking=profile_dict.get("smoking_drinking", "No Smoking/Drinking"),
        dietary_restrictions=profile_dict.get("dietary_restrictions", "No Restrictions"),
    )

    # Load candidates and interactions and compute recommendations
    users = load_users()
    interactions = get_user_interactions(custom_user.id)
    engine = RecommendationEngine()
    matches = engine.recommend(custom_user, users, limit=6, interactions=interactions)

    # Minimal liked/saved sections (can be populated from interactions)
    liked = []
    saved = []

    # Broadcast a notification to connected websocket clients
    await manager.broadcast({
        "type": "NEW_MATCH", 
        "message": f"Custom profile updated for {profile_dict.get('name', 'user')}!"
    })

    # Return the shape expected by the frontend
    return {
        "user": profile_dict,
        "matches": matches,
        "liked": liked,
        "saved": saved,
    }


# Simple interaction recorder used by the frontend (like/save/skip)
@app.post("/api/interactions")
async def save_interaction(payload: dict):
    try:
        from src.interactions import record_interaction
        user_id = int(payload.get("user_id", 0) or 0)
        candidate_id = int(payload.get("candidate_id", 0) or 0)
        action = payload.get("action", "like")
        record_interaction(user_id, candidate_id, action)
        return {"status": "saved", "action": action, "candidate_id": candidate_id}
    except Exception:
        return {"status": "error"}


# OAuth login start
@app.get("/login/{provider}")
async def login(request: Request, provider: str):
    if provider not in ("github", "google"):
        return RedirectResponse("/")
    client = oauth.create_client(provider)
    redirect_uri = request.url_for("auth", provider=provider)
    return await client.authorize_redirect(request, str(redirect_uri))


# OAuth callback
@app.get("/auth/{provider}")
async def auth(request: Request, provider: str):
    if provider not in ("github", "google"):
        return RedirectResponse("/")
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)
    if provider == "github":
        resp = await client.get("user", token=token)
        profile = resp.json()
        name = profile.get("login") or profile.get("name")
    else:
        resp = await client.get("userinfo", token=token)
        profile = resp.json()
        name = profile.get("name") or profile.get("email")

    # create persistent session and set session id in cookie-backed session
    user_obj = {"name": name, "provider": provider, "profile": profile}
    sid = create_persistent_session(user_obj)
    request.session["session_id"] = sid
    request.session["user"] = {"name": name, "provider": provider}

    # redirect to frontend root
    return RedirectResponse(url="/")


# Handle root page and custom paths explicitly to avoid matching the WebSocket path
@app.get("/{path:path}")
async def serve_frontend(path: str = ""):
    if not path:
        path = "index.html"
    
    file_path = os.path.join("web", path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    return FileResponse(os.path.join("web", "index.html"))


# Logout endpoint to clear persistent session and cookie session
@app.post("/api/logout")
async def logout(request: Request):
    sid = request.session.get("session_id")
    if sid:
        delete_persistent_session(sid)
    request.session.clear()
    return {"status": "ok"}


# Optional session info endpoint for frontend UI updates
@app.get("/api/session")
async def get_session(request: Request):
    # Prefer persisted session if available
    sid = request.session.get("session_id")
    if sid:
        sessions = load_sessions()
        sess = sessions.get(sid)
        if sess and isinstance(sess, dict) and sess.get("user"):
            user = sess.get("user")
            return {"user": {"name": user.get("name"), "provider": user.get("provider")}}

    # Fallback to in-memory session info
    user = request.session.get("user")
    if not user:
        return {"user": None}
    return {"user": {"name": user.get("name"), "provider": user.get("provider")}}
