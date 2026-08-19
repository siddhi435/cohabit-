import os


def build_explanation(user, candidate):
    reasons = []

    if user.city != "Unknown" and user.city == candidate.city:
        reasons.append("same city")

    if user.budget and candidate.budget and abs(user.budget - candidate.budget) <= 3000:
        reasons.append("similar budget")

    if user.preferred_gender != "Any" and candidate.gender == user.preferred_gender:
        reasons.append(f"matches preferred roommate gender ({user.preferred_gender})")

    if user.sleep_schedule == candidate.sleep_schedule:
        reasons.append("similar sleep schedule")

    if user.cleanliness == candidate.cleanliness:
        reasons.append("same cleanliness preference")

    if user.work_shift == candidate.work_shift:
        reasons.append("same work shift")

    if user.personality == candidate.personality:
        reasons.append("similar personality")

    if user.noise_preference == candidate.noise_preference:
        reasons.append("same noise preference")

    if abs(user.social_energy_rating - candidate.social_energy_rating) <= 1:
        reasons.append("similar social energy")

    if user.room_type_preference == candidate.room_type_preference:
        reasons.append("same room type preference")

    if user.privacy_importance == candidate.privacy_importance:
        reasons.append("similar privacy needs")

    if user.pets == candidate.pets:
        reasons.append("compatible pet preference")

    if (
        user.smoking_drinking == "No Smoking/Drinking"
        and candidate.smoking_drinking not in ["Smoker", "Drinker"]
    ):
        reasons.append("respects no smoking or drinking preference")
    elif user.smoking_drinking == candidate.smoking_drinking:
        reasons.append("compatible smoking or drinking preference")

    if user.dietary_restrictions == candidate.dietary_restrictions:
        reasons.append("similar dietary preference")

    if not reasons:
        return "Different preferences, but may still be worth exploring."

    return "Match reasons: " + ", ".join(reasons) + "."


def build_match_coach(user, candidate, score):
    if score >= 85:
        guidance = "This feels like a strong fit. Keep the conversation focused on routines, guests, and shared-space expectations."
    elif score >= 70:
        guidance = "This is a dependable match. A quick chat about schedules and household habits should seal the deal."
    else:
        guidance = "This is a promising starter match. Ask about preferred study hours, guests, and weekend routines before deciding."

    return f"{guidance} Coach note: {candidate.name} likely values calm, predictable habits that align with your profile."


def build_llm_explanation(user, candidate, score):
    base = build_explanation(user, candidate)
    coach = build_match_coach(user, candidate, score)

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": "You are a friendly roommate matching assistant.",
                    },
                    {
                        "role": "user",
                        "content": f"Explain why {candidate.name} is a good roommate match for {user.name} in 2-3 sentences.",
                    },
                ],
                temperature=0.4,
            )
            if getattr(response, "output_text", ""):
                return response.output_text.strip()
        except Exception:
            pass

    return f"{base} {coach}"
