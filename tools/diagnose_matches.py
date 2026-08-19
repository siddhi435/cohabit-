from src.main import load_users
from src.recommender import RecommendationEngine
from src.interactions import get_user_interactions


def diagnose(user_index=0):
    users = load_users()
    user = users[user_index]
    engine = RecommendationEngine()
    interactions = get_user_interactions(user.id)

    print('Diagnosing for user:', user.name, user.gender, user.smoking_drinking)
    for cand in users:
        if cand.id == user.id:
            continue
        reasons = []
        if not engine.gender_matches(user, cand):
            reasons.append('gender_mismatch')
        if not engine.smoking_drinking_matches(user, cand):
            reasons.append('smoking_drinking_mismatch')
        last_action = engine._last_interaction_for_candidate(cand, interactions)
        if last_action == 'skip':
            reasons.append('skipped_by_user')
        if not reasons:
            print(f"CAND {cand.id} {cand.name}: INCLUDED (score {engine.match_score(user,cand)})")
        else:
            print(f"CAND {cand.id} {cand.name}: FILTERED -> {', '.join(reasons)}")


if __name__ == '__main__':
    diagnose()
