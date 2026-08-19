import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from src.explain import build_explanation, build_llm_explanation


class RecommendationEngine:
    def __init__(self, use_transformers=False):
        self.model = None

        if use_transformers:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except (ImportError, Exception):
                self.model = None

    def _normalize_text(self, value):
        return re.sub(r"[^a-z0-9]+", " ", str(value or "")).strip().lower()

    def extract_traits_from_bio(self, bio):
        if not bio:
            return []

        lower = self._normalize_text(bio)
        traits = set()

        keyword_map = {
            "introvert": "introvert",
            "extrovert": "extrovert",
            "quiet": "quiet",
            "noisy": "noisy",
            "morning": "morning",
            "evening": "evening",
            "night": "night",
            "vegetarian": "vegetarian",
            "non vegetarian": "non-vegetarian",
            "jain": "jain",
            "private": "private",
            "shared": "shared",
            "organized": "organized",
            "messy": "messy",
            "pet": "pet-friendly",
            "pets": "pet-friendly",
            "dog": "pet-friendly",
            "cat": "pet-friendly",
            "smoker": "smoker",
            "drinker": "drinker",
            "calm": "calm",
            "social": "social",
            "early": "early-riser",
            "late": "night-owl",
        }

        for phrase, trait in keyword_map.items():
            if phrase in lower:
                traits.add(trait)

        return sorted(traits)

    def _profile_traits(self, user):
        traits = set(self.extract_traits_from_bio(user.bio))

        for value in [
            user.personality,
            user.noise_preference,
            user.dietary_restrictions,
            user.work_shift,
            user.room_type_preference,
            user.privacy_importance,
            user.sleep_schedule,
        ]:
            normalized = self._normalize_text(value)
            if normalized:
                traits.add(normalized)

        if user.pets and user.pets != "No Pets":
            traits.add("pet-friendly")

        return traits

    def constraint_score(self, user, candidate):
        if not self.gender_matches(user, candidate):
            return 0

        if not self.smoking_drinking_matches(user, candidate):
            return 0

        return 10

    def lifestyle_score(self, user, candidate):
        score = 0

        if user.city != "Unknown" and user.city == candidate.city:
            score += 12

        if user.budget and candidate.budget:
            budget_difference = abs(user.budget - candidate.budget)
            if budget_difference <= 2000:
                score += 12
            elif budget_difference <= 5000:
                score += 6

        if user.sleep_schedule == candidate.sleep_schedule:
            score += 6

        if user.cleanliness == candidate.cleanliness:
            score += 7

        if user.work_shift == candidate.work_shift:
            score += 4

        if user.personality == candidate.personality:
            score += 4

        if user.noise_preference == candidate.noise_preference:
            score += 6

        if abs(user.social_energy_rating - candidate.social_energy_rating) <= 1:
            score += 5

        if user.room_type_preference == candidate.room_type_preference:
            score += 4

        if user.privacy_importance == candidate.privacy_importance:
            score += 4

        if user.pets == candidate.pets:
            score += 3

        if user.smoking_drinking == candidate.smoking_drinking:
            score += 3

        if user.dietary_restrictions == candidate.dietary_restrictions:
            score += 4

        return round(min(60, score), 2)

    def bio_similarity_score(self, user, candidate):
        if self.model is None:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([user.bio, candidate.bio])
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

            return float(similarity) * 20

        embeddings = self.model.encode([user.bio, candidate.bio])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        return float(similarity) * 20

    def trait_overlap_score(self, user, candidate):
        user_traits = self._profile_traits(user)
        candidate_traits = self._profile_traits(candidate)
        overlap = len(user_traits & candidate_traits)
        return round(min(20, overlap * 4), 2)

    def text_score(self, user, candidate):
        bio_similarity = self.bio_similarity_score(user, candidate)
        trait_overlap = self.trait_overlap_score(user, candidate)
        return round(min(30, bio_similarity + trait_overlap), 2)

    def match_score(self, user, candidate):
        constraints = self.constraint_score(user, candidate)
        lifestyle = self.lifestyle_score(user, candidate)
        text = self.text_score(user, candidate)

        total = constraints + lifestyle + text
        return round(min(total, 100), 2)

    def gender_matches(self, user, candidate):
        if user.gender == "Female":
            return candidate.gender == "Female"
        
        if user.gender == "Male":
            return candidate.gender == "Male"

        required_gender = user.preferred_gender
        if required_gender == "Any":
            return True

        return candidate.gender == required_gender

    def smoking_drinking_matches(self, user, candidate):
        if user.smoking_drinking != "No Smoking/Drinking":
            return True

        return candidate.smoking_drinking not in ["Smoker", "Drinker"]

    def interaction_boost(self, user, candidate, interactions=None):
        if not interactions:
            return 0

        action_weights = {"like": 8, "save": 6, "skip": -4}
        score = 0

        for interaction in interactions:
            if interaction.get("candidate_id") != candidate.id:
                continue
            action = interaction.get("action", "skip")
            score += action_weights.get(action, 0)

        return round(min(10, max(0, score)), 2)

    def collaborative_filtering_score(self, user, candidate, interactions=None):
        if not interactions:
            return 0

        try:
            from lightfm import LightFM
            from scipy.sparse import csr_matrix
        except Exception:
            return self._simple_collaborative_score(user, candidate, interactions)

        relevant_interactions = [
            interaction for interaction in interactions if interaction.get("action") in {"like", "save"}
        ]

        if len(relevant_interactions) < 2:
            return self._simple_collaborative_score(user, candidate, interactions)

        user_ids = sorted({interaction["user_id"] for interaction in relevant_interactions})
        candidate_ids = sorted({interaction["candidate_id"] for interaction in relevant_interactions})

        if user.id not in user_ids:
            user_ids.append(user.id)
        if candidate.id not in candidate_ids:
            candidate_ids.append(candidate.id)

        user_index = {user_id: index for index, user_id in enumerate(user_ids)}
        item_index = {candidate_id: index for index, candidate_id in enumerate(candidate_ids)}

        rows = []
        cols = []
        data = []
        for interaction in relevant_interactions:
            user_id = interaction.get("user_id")
            candidate_id = interaction.get("candidate_id")
            if user_id in user_index and candidate_id in item_index:
                rows.append(user_index[user_id])
                cols.append(item_index[candidate_id])
                data.append(1.0)

        if not data:
            return 0

        matrix = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(candidate_ids)))

        model = LightFM(loss="warp", random_state=42)
        model.fit(matrix, epochs=20, num_threads=2)
        user_row = user_index.get(user.id)
        item_idx = item_index.get(candidate.id)

        if user_row is None or item_idx is None:
            return 0

        score = model.predict(user_row, np.array([item_idx]))[0]
        return round(min(10, max(0, score * 2.5)), 2)

    def _simple_collaborative_score(self, user, candidate, interactions=None):
        if not interactions:
            return 0

        liked_by_user = {
            interaction.get("candidate_id")
            for interaction in interactions
            if interaction.get("user_id") == user.id and interaction.get("action") in {"like", "save"}
        }

        if not liked_by_user:
            return 0

        scores = []
        for interaction in interactions:
            if interaction.get("user_id") == user.id or interaction.get("action") not in {"like", "save"}:
                continue
            if interaction.get("candidate_id") != candidate.id:
                continue
            other_user_id = interaction.get("user_id")
            other_user_likes = {
                item.get("candidate_id")
                for item in interactions
                if item.get("user_id") == other_user_id and item.get("action") in {"like", "save"}
            }
            overlap = len(liked_by_user & other_user_likes)
            if overlap:
                scores.append(overlap)

        if not scores:
            return 0

        return round(min(10, sum(scores) / 2), 2)

    def infer_persona_label(self, user):
        traits = self._profile_traits(user)

        if "introvert" in traits and "quiet" in traits:
            return "Quiet Planner"

        if "extrovert" in traits and "noisy" in traits:
            return "Social Spark"

        if "morning" in traits and "organized" in traits:
            return "Early Riser"

        if "pet-friendly" in traits:
            return "Pet-Friendly Neighbor"

        if "vegetarian" in traits:
            return "Balanced Host"

        return "Balanced Roommate"

    def infer_cluster_label(self, user):
        traits = self._profile_traits(user)

        if "introvert" in traits and "quiet" in traits:
            return "Quiet Cohort"

        if "extrovert" in traits or "social" in traits:
            return "Social Cohort"

        if "pet-friendly" in traits:
            return "Pet-Friendly Cluster"

        if "vegetarian" in traits:
            return "Balanced Cluster"

        return "Mixed Cluster"

    def _last_interaction_for_candidate(self, candidate, interactions):
        if not interactions:
            return None

        history = [interaction for interaction in interactions if interaction.get("candidate_id") == candidate.id]
        if not history:
            return None

        return sorted(history, key=lambda item: item.get("timestamp", ""))[-1].get("action")

    def recommend(self, user, candidates, limit=5, interactions=None):
        matches = []

        for candidate in candidates:
            if candidate.id == user.id:
                continue

            if not self.gender_matches(user, candidate):
                continue

            if not self.smoking_drinking_matches(user, candidate):
                continue

            candidate_action = self._last_interaction_for_candidate(candidate, interactions)
            if candidate_action == "skip":
                continue

            score = self.match_score(user, candidate)
            score += self.interaction_boost(user, candidate, interactions)
            score += self.collaborative_filtering_score(user, candidate, interactions)
            score = round(min(score, 100), 2)

            traits = sorted(self._profile_traits(candidate))
            persona = self.infer_persona_label(candidate)
            cluster = self.infer_cluster_label(candidate)
            explanation = build_explanation(user, candidate)
            coach = build_llm_explanation(user, candidate, score)
            status = candidate_action if candidate_action in {"like", "save"} else None

            matches.append({
                "id": candidate.id,
                "name": candidate.name,
                "score": score,
                "explanation": explanation,
                "coach": coach,
                "persona": persona,
                "cluster": cluster,
                "traits": traits,
                "status": status,
            })

        matches.sort(key=lambda item: item["score"], reverse=True)

        return matches[:limit]
