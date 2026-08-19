import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models import UserProfile
from src.recommender import RecommendationEngine


CSV_PATH = Path("data/Girls_pg_hostel_CSV_data-1.csv")
JSON_PATH = Path("data/user.json")
NEW_PROFILE_ID = 0


def load_users_from_json():
    with open("data/user.json", "r") as file:
        raw_users = json.load(file)

    return [UserProfile(**user) for user in raw_users]


def load_users_from_csv():
    users = []

    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader, start=1):
            bio = (
                f"{row['user_name']} works as a {row['profession']} with a "
                f"{row['work_shift'].lower()} shift. They are {row['personality'].lower()}, "
                f"prefer a {row['noise_preference'].lower()} home, want a "
                f"{row['room_type_preference'].lower()}, have {row['privacy_importance'].lower()} "
                f"privacy needs, and follow {row['dietary_restrictions'].lower()} food preferences."
            )

            users.append(UserProfile(
                id=index,
                name=row["user_name"],
                gender="Female",
                preferred_gender="Any",
                cleanliness=row["cleanliness"],
                sleep_schedule=row["sleep_type"],
                guests=row["social_energy_rating"],
                smoking=row["smoking_drinking"] == "Smoker",
                bio=bio,
                work_shift=row["work_shift"],
                profession=row["profession"],
                personality=row["personality"],
                bedtime=row["bedtime"],
                wake_time=row["wake_time"],
                sleep_type=row["sleep_type"],
                noise_preference=row["noise_preference"],
                social_energy_rating=int(row["social_energy_rating"]),
                room_type_preference=row["room_type_preference"],
                privacy_importance=row["privacy_importance"],
                pets=row["pets"],
                smoking_drinking=row["smoking_drinking"],
                dietary_restrictions=row["dietary_restrictions"],
            ))

    return users


def load_users():
    if CSV_PATH.exists():
        return load_users_from_csv()

    return load_users_from_json()


def ask_choice(label, options):
    print(label)

    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    while True:
        answer = input("Choose a number: ").strip()

        if answer.isdigit():
            selected_index = int(answer) - 1
            if 0 <= selected_index < len(options):
                return options[selected_index]

        print("Please choose one of the listed numbers.")


def ask_number(label, minimum, maximum):
    while True:
        answer = input(f"{label} ({minimum}-{maximum}): ").strip()

        if answer.isdigit():
            value = int(answer)
            if minimum <= value <= maximum:
                return value

        print(f"Please enter a number between {minimum} and {maximum}.")


def create_profile_from_input():
    print("Create your CoHabit profile")
    print()

    name = input("Your name: ").strip() or "You"
    profession = input("Your profession: ").strip() or "Student"
    gender = ask_choice("Your gender:", ["Female", "Male", "Other"])
    preferred_gender = ask_choice("Preferred roommate gender:", ["Female", "Male", "Any"])
    work_shift = ask_choice("Work/study shift:", ["Morning", "Evening", "Night"])
    personality = ask_choice("Personality:", ["Introvert", "Extrovert"])
    cleanliness = ask_choice("Cleanliness:", ["Organised", "Messy", "Both"])
    bedtime = input("Bedtime, example 11 PM: ").strip() or "11 PM"
    wake_time = input("Wake time, example 7 AM: ").strip() or "7 AM"
    sleep_type = ask_choice("Sleep type:", ["Light Sleeper", "Heavy Sleeper"])
    noise_preference = ask_choice("Noise preference:", ["Quiet", "Noisy"])
    social_energy_rating = ask_number("Social energy rating", 1, 5)
    room_type_preference = ask_choice("Room type preference:", ["Private Room", "Shared Room"])
    privacy_importance = ask_choice("Privacy importance:", ["Low", "Medium", "High"])
    pets = ask_choice("Pets:", ["No Pets", "Has Dog", "Has Cat"])
    smoking_drinking = ask_choice(
        "Smoking/drinking preference:",
        ["Okay with Roommate's Habits", "Smoker", "Drinker", "No Smoking/Drinking"],
    )
    dietary_restrictions = ask_choice(
        "Dietary preference:",
        ["No Restrictions", "Vegetarian", "Non-Vegetarian", "Jain"],
    )
    bio = input("Brief bio or lifestyle note: ").strip() or (
        f"{name} works as a {profession} with a {work_shift.lower()} shift. "
        f"They are {personality.lower()}, prefer a {noise_preference.lower()} home, "
        f"want a {room_type_preference.lower()}, have {privacy_importance.lower()} "
        f"privacy needs, and follow {dietary_restrictions.lower()} food preferences."
    )

    return UserProfile(
        id=NEW_PROFILE_ID,
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


def print_matches(current_user, matches):
    print(f"Top matches for {current_user.name}:")
    print()

    for match in matches:
        print(f"{match['name']} - {match['score']}%")
        print(f"Why: {match['explanation']}")
        print()


def main():
    users = load_users()

    mode = ask_choice(
        "What do you want to do?",
        ["Create my own profile", "Use first profile from dataset"],
    )

    if mode == "Create my own profile":
        print()
        current_user = create_profile_from_input()
    else:
        current_user = users[0]

    engine = RecommendationEngine()
    matches = engine.recommend(current_user, users)

    print()
    print_matches(current_user, matches)


if __name__ == "__main__":
    main()
