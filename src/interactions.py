from pathlib import Path
from typing import Any, Dict, List
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.explain import build_explanation
from src.recommender import RecommendationEngine

INTERACTIONS_PATH = Path("data/interactions.json")
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


INTERACTIONS_PATH = Path("data/interactions.json")


def load_interactions() -> List[Dict[str, Any]]:
    if not INTERACTIONS_PATH.exists():
        return []

    with INTERACTIONS_PATH.open("r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_interactions(interactions: List[Dict[str, Any]]) -> None:
    INTERACTIONS_PATH.parent.mkdir(exist_ok=True)

    with INTERACTIONS_PATH.open("w", encoding="utf-8") as file:
        json.dump(interactions, file, indent=2)


def record_interaction(user_id: int, candidate_id: int, action: str) -> List[Dict[str, Any]]:
    interactions = load_interactions()
    interactions.append(
        {
            "user_id": int(user_id),
            "candidate_id": int(candidate_id),
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_interactions(interactions)
    return interactions


def get_user_interactions(user_id: int) -> List[Dict[str, Any]]:
    return [interaction for interaction in load_interactions() if interaction.get("user_id") == int(user_id)]

def build_retrieval_context(user, candidates: List[Any], top_k: int = 3) -> List[Dict[str, Any]]:
    """Return top-k candidates most similar to the user's bio using TF-IDF as a simple retriever.

    The returned list contains dicts with `id`, `name`, and `snippet` keys.
    """
    docs = [candidate.bio or "" for candidate in candidates]
    if not any(docs):
        return []

    vectorizer = TfidfVectorizer().fit(docs + [user.bio or ""])
    candidate_vecs = vectorizer.transform(docs)
    user_vec = vectorizer.transform([user.bio or ""])

    sims = cosine_similarity(user_vec, candidate_vecs)[0]
    ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for idx, score in ranked:
        cand = candidates[idx]
        snippet = (cand.bio or "").strip()
        results.append({"id": cand.id, "name": cand.name, "snippet": snippet, "score": float(score)})

    return results

def rag_chat(user, candidates: List[Any], question: str, top_k: int = 3) -> str:
    """Simple RAG-style assistant. If `OPENAI_API_KEY` is set, forwards to the API; otherwise returns a heuristic answer.

    Uses `RecommendationEngine.recommend` to pick top candidates and `build_explanation` for reasons.
    """
    # first, get recommended candidates with current interaction history
    engine = RecommendationEngine(use_transformers=False)
    interactions = get_user_interactions(user.id)
    recs = engine.recommend(user, candidates, limit=top_k, interactions=interactions)

    if not recs:
        return "I couldn't find clear matches right now. Try expanding your preferences."

    # Build a short context from top recommendations
    context_lines = []
    for r in recs:
        # find candidate object
        cand_obj = next((c for c in candidates if c.id == r["id"]), None)
        reason = build_explanation(user, cand_obj) if cand_obj else r.get("explanation", "")
        context_lines.append(f"{r['name']}: {reason}")

    context_text = "\n".join(context_lines)

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            prompt = (
                f"You are a helpful roommate assistant. The user asked: {question}\n"
                f"Here are top candidate contexts:\n{context_text}\n"
                f"Answer succinctly in 2-3 sentences and suggest next steps."
            )
            response = client.responses.create(model="gpt-4o-mini", input=[{"role": "user", "content": prompt}], temperature=0.3)
            if getattr(response, "output_text", ""):
                return response.output_text.strip()
        except Exception:
            # fall through to local answer
            pass

    # Local fallback answer
    names = ", ".join([r["name"] for r in recs])
    answer = f"I found these promising matches: {names}.\nContext:\n{context_text}\n"
    answer += f"About your question: {question}\nSuggested next step: message the top match to ask about routines and guests."
    return answer
