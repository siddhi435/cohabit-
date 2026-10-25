import streamlit as st

from src.main import load_users
from src.models import UserProfile
from src.recommender import RecommendationEngine


@st.cache_resource
def get_matching_data():
    return load_users(), RecommendationEngine()


def build_profile(values):
    name = values["name"].strip() or "You"
    profession = values["profession"].strip() or "Student"
    bio = values["bio"].strip() or (
        f"{name} works as a {profession} with a {values['work_shift'].lower()} shift. "
        f"They are {values['personality'].lower()}, prefer a "
        f"{values['noise_preference'].lower()} home, want a "
        f"{values['room_type_preference'].lower()}, have "
        f"{values['privacy_importance'].lower()} privacy needs, and follow "
        f"{values['dietary_restrictions'].lower()} food preferences."
    )

    return UserProfile(
        id=0,
        name=name,
        gender=values["gender"],
        preferred_gender=values["preferred_gender"],
        cleanliness=values["cleanliness"],
        sleep_schedule=values["sleep_type"],
        guests=str(values["social_energy_rating"]),
        smoking=values["smoking_drinking"] == "Smoker",
        bio=bio,
        work_shift=values["work_shift"],
        profession=profession,
        personality=values["personality"],
        bedtime=values["bedtime"].strip() or "11 PM",
        wake_time=values["wake_time"].strip() or "7 AM",
        sleep_type=values["sleep_type"],
        noise_preference=values["noise_preference"],
        social_energy_rating=values["social_energy_rating"],
        room_type_preference=values["room_type_preference"],
        privacy_importance=values["privacy_importance"],
        pets=values["pets"],
        smoking_drinking=values["smoking_drinking"],
        dietary_restrictions=values["dietary_restrictions"],
    )


def main():
    st.set_page_config(page_title="CoHabit | Roommate Matches", page_icon="🏠")
    st.title("CoHabit")
    st.subheader("Find your kind of home")
    st.write("Tell us how you like to live to see compatible roommate recommendations.")

    with st.form("roommate_preferences"):
        st.subheader("Your profile")
        name = st.text_input("Name")
        profession = st.text_input("Profession", value="Student")
        gender = st.selectbox("Your gender", ["Female", "Male", "Other"])
        preferred_gender = st.selectbox(
            "Preferred roommate gender", ["Any", "Female", "Male"]
        )

        left, right = st.columns(2)
        with left:
            work_shift = st.selectbox("Work or study shift", ["Morning", "Evening", "Night"])
            personality = st.selectbox("Personality", ["Introvert", "Extrovert"])
            cleanliness = st.selectbox("Cleanliness", ["Organised", "Messy", "Both"])
            bedtime = st.text_input("Bedtime", value="11 PM")
            sleep_type = st.selectbox("Sleep type", ["Light Sleeper", "Heavy Sleeper"])
            noise_preference = st.selectbox("Noise preference", ["Quiet", "Noisy"])
            social_energy_rating = st.slider("Social energy", 1, 5, 3)
        with right:
            wake_time = st.text_input("Wake time", value="7 AM")
            room_type_preference = st.selectbox(
                "Room type", ["Private Room", "Shared Room"]
            )
            privacy_importance = st.selectbox(
                "Privacy importance", ["Low", "Medium", "High"]
            )
            pets = st.selectbox("Pets", ["No Pets", "Has Dog", "Has Cat"])
            smoking_drinking = st.selectbox(
                "Smoking/drinking preference",
                [
                    "No Smoking/Drinking",
                    "Okay with Roommate's Habits",
                    "Smoker",
                    "Drinker",
                ],
            )
            dietary_restrictions = st.selectbox(
                "Dietary preference",
                ["No Restrictions", "Vegetarian", "Non-Vegetarian", "Jain"],
            )

        bio = st.text_area("About your lifestyle (optional)")
        submitted = st.form_submit_button("Find my matches", type="primary")

    if submitted:
        profile = build_profile(
            {
                "name": name,
                "profession": profession,
                "gender": gender,
                "preferred_gender": preferred_gender,
                "work_shift": work_shift,
                "personality": personality,
                "cleanliness": cleanliness,
                "bedtime": bedtime,
                "wake_time": wake_time,
                "sleep_type": sleep_type,
                "noise_preference": noise_preference,
                "social_energy_rating": social_energy_rating,
                "room_type_preference": room_type_preference,
                "privacy_importance": privacy_importance,
                "pets": pets,
                "smoking_drinking": smoking_drinking,
                "dietary_restrictions": dietary_restrictions,
                "bio": bio,
            }
        )
        users, engine = get_matching_data()
        st.session_state["matches"] = engine.recommend(profile, users, limit=6)
        st.session_state["profile_name"] = profile.name

    if "matches" in st.session_state:
        st.subheader(f"Top roommate matches for {st.session_state['profile_name']}")
        if not st.session_state["matches"]:
            st.info("No compatible profiles found. Try adjusting your preferences.")
        for match in st.session_state["matches"]:
            with st.container(border=True):
                st.markdown(f"### {match['name']}")
                st.progress(match["score"] / 100, text=f"{match['score']}% compatibility")
                st.write(match["explanation"])
                st.caption(match["coach"])
                if match["traits"]:
                    st.caption("Lifestyle traits: " + ", ".join(match["traits"]))


if __name__ == "__main__":
    main()
