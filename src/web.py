import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.interactions import get_user_interactions, record_interaction
from src.main import load_users
from src.models import UserProfile
from src.recommender import RecommendationEngine
from src.explain import build_explanation, build_llm_explanation


HOST = "127.0.0.1"
PORT = 8000
WEB_ROOT = Path("web")


class CoHabitRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/users":
            self.send_json(get_users_response())
            return

        if parsed_url.path == "/api/matches":
            query = parse_qs(parsed_url.query)
            user_id = int(query.get("user_id", ["1"])[0])
            self.send_json(get_matches_response(user_id))
            return

        if parsed_url.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/custom-matches":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
            self.send_json(get_custom_matches_response(payload))
            return

        if parsed_url.path == "/api/interactions":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
            self.send_json(save_interaction(payload))
            return

        self.send_error(404, "Not found")

    def send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def user_to_dict(user):
    return {
        "id": user.id,
        "name": user.name,
        "gender": user.gender,
        "preferred_gender": user.preferred_gender,
        "profession": user.profession,
        "work_shift": user.work_shift,
        "personality": user.personality,
        "cleanliness": user.cleanliness,
        "sleep_type": user.sleep_type,
        "noise_preference": user.noise_preference,
        "room_type_preference": user.room_type_preference,
        "privacy_importance": user.privacy_importance,
        "pets": user.pets,
        "smoking_drinking": user.smoking_drinking,
        "dietary_restrictions": user.dietary_restrictions,
        "bio": user.bio,
        "traits": getattr(user, "traits", []),
        "persona": getattr(user, "persona_label", ""),
    }


def get_users_response():
    users = load_users()
    return {"users": [user_to_dict(user) for user in users]}


def _build_interaction_sections(user, candidates, interactions):
    engine = RecommendationEngine()
    liked = []
    saved = []

    for candidate in candidates:
        if candidate.id == user.id:
            continue

        action = _last_candidate_action(candidate.id, interactions)
        if action not in {"like", "save"}:
            continue

        score = engine.match_score(user, candidate)
        score += engine.interaction_boost(user, candidate, interactions)
        score += engine.collaborative_filtering_score(user, candidate, interactions)
        score = round(min(score, 100), 2)

        entry = {
            "id": candidate.id,
            "name": candidate.name,
            "score": score,
            "explanation": build_explanation(user, candidate),
            "coach": build_llm_explanation(user, candidate, score),
            "persona": engine.infer_persona_label(candidate),
            "cluster": engine.infer_cluster_label(candidate),
            "traits": sorted(engine._profile_traits(candidate)),
            "status": action,
        }

        if action == "like":
            liked.append(entry)
        elif action == "save":
            saved.append(entry)

    return liked, saved


def _last_candidate_action(candidate_id, interactions):
    history = [interaction for interaction in interactions if interaction.get("candidate_id") == candidate_id]
    if not history:
        return None

    return sorted(history, key=lambda item: item.get("timestamp", ""))[-1].get("action")


def get_matches_response(user_id):
    users = load_users()
    current_user = next((user for user in users if user.id == user_id), users[0])
    interactions = get_user_interactions(user_id)
    engine = RecommendationEngine()
    matches = engine.recommend(current_user, users, limit=6, interactions=interactions)
    liked, saved = _build_interaction_sections(current_user, users, interactions)

    return {
        "user": user_to_dict(current_user),
        "matches": matches,
        "liked": liked,
        "saved": saved,
    }


def get_custom_matches_response(payload):
    users = load_users()
    custom_user = build_custom_user(payload)
    interactions = get_user_interactions(custom_user.id)
    engine = RecommendationEngine()
    matches = engine.recommend(custom_user, users, limit=6, interactions=interactions)
    liked, saved = _build_interaction_sections(custom_user, users, interactions)

    return {
        "user": user_to_dict(custom_user),
        "matches": matches,
        "liked": liked,
        "saved": saved,
    }


def save_interaction(payload):
    user_id = int(payload.get("user_id", 0) or 0)
    candidate_id = int(payload.get("candidate_id", 0) or 0)
    action = payload.get("action", "like")
    record_interaction(user_id, candidate_id, action)
    return {"status": "saved", "action": action, "candidate_id": candidate_id}


def build_custom_user(payload):
    name = payload.get("name") or "You"
    profession = payload.get("profession") or "Student"
    gender = payload.get("gender") or "Female"
    preferred_gender = payload.get("preferred_gender") or "Any"
    work_shift = payload.get("work_shift") or "Morning"
    personality = payload.get("personality") or "Introvert"
    cleanliness = payload.get("cleanliness") or "Organised"
    bedtime = payload.get("bedtime") or "11 PM"
    wake_time = payload.get("wake_time") or "7 AM"
    sleep_type = payload.get("sleep_type") or "Light Sleeper"
    noise_preference = payload.get("noise_preference") or "Quiet"
    social_energy_rating = int(payload.get("social_energy_rating") or 3)
    room_type_preference = payload.get("room_type_preference") or "Private Room"
    privacy_importance = payload.get("privacy_importance") or "Medium"
    pets = payload.get("pets") or "No Pets"
    smoking_drinking = payload.get("smoking_drinking") or "Okay with Roommate's Habits"
    dietary_restrictions = payload.get("dietary_restrictions") or "No Restrictions"
    bio = payload.get("bio") or (
        f"{name} works as a {profession} with a {work_shift.lower()} shift. "
        f"They are {personality.lower()}, prefer a {noise_preference.lower()} home, "
        f"want a {room_type_preference.lower()}, have {privacy_importance.lower()} "
        f"privacy needs, and follow {dietary_restrictions.lower()} food preferences."
    )

    return UserProfile(
        id=0,
        name=name,
        gender=gender,
        preferred_gender=preferred_gender,
        cleanliness=cleanliness,
        sleep_schedule=sleep_type,
        guests=str(social_energy_rating),
        smoking=smoking_drinking == "Smoker",
        bio=bio,
        work_shift=work_shift,
        profession=profession,
        personality=personality,
        bedtime=bedtime,
        wake_time=wake_time,
        sleep_type=sleep_type,
        noise_preference=noise_preference,
        social_energy_rating=social_energy_rating,
        room_type_preference=room_type_preference,
        privacy_importance=privacy_importance,
        pets=pets,
        smoking_drinking=smoking_drinking,
        dietary_restrictions=dietary_restrictions,
    )


def roommate_gender_for(gender):
    if gender in ["Female", "Male"]:
        return gender

    return "Any"


def main():
    server = ThreadingHTTPServer((HOST, PORT), CoHabitRequestHandler)
    print(f"CoHabit site running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
