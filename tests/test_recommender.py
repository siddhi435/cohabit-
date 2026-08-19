import unittest

from src.models import UserProfile
from src.recommender import RecommendationEngine


class RecommendationEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = RecommendationEngine(use_transformers=False)

    def test_extract_traits_from_bio(self):
        traits = self.engine.extract_traits_from_bio(
            "I am introverted, love quiet evenings, early mornings, and vegetarian food"
        )
        self.assertIn("introvert", traits)
        self.assertIn("quiet", traits)
        self.assertIn("vegetarian", traits)

    def test_match_score_uses_trait_overlap(self):
        user = UserProfile(
            id=1,
            name="You",
            bio="I am introverted, love quiet evenings, early mornings, and vegetarian food",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="3",
            smoking=False,
            work_shift="Morning",
            profession="Student",
            personality="Introvert",
            bedtime="11 PM",
            wake_time="7 AM",
            sleep_type="Light Sleeper",
            noise_preference="Quiet",
            social_energy_rating=2,
            room_type_preference="Private Room",
            privacy_importance="High",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="Vegetarian",
        )
        candidate = UserProfile(
            id=2,
            name="Ava",
            bio="I am introverted, enjoy quiet evenings, early mornings, and vegetarian meals",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="2",
            smoking=False,
            work_shift="Morning",
            profession="Designer",
            personality="Introvert",
            bedtime="11 PM",
            wake_time="7 AM",
            sleep_type="Light Sleeper",
            noise_preference="Quiet",
            social_energy_rating=2,
            room_type_preference="Private Room",
            privacy_importance="High",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="Vegetarian",
        )

        lifestyle_score = self.engine.lifestyle_score(user, candidate)
        trait_score = self.engine.trait_overlap_score(user, candidate)
        total = self.engine.match_score(user, candidate)

        self.assertGreater(trait_score, 0)
        self.assertGreater(total, lifestyle_score)

    def test_female_user_only_sees_female_matches(self):
        user = UserProfile(
            id=1,
            name="Sara",
            bio="I like quiet evenings and shared rooms",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="2",
            smoking=False,
            work_shift="Morning",
            profession="Student",
            personality="Introvert",
            bedtime="11 PM",
            wake_time="7 AM",
            sleep_type="Light Sleeper",
            noise_preference="Quiet",
            social_energy_rating=3,
            room_type_preference="Private Room",
            privacy_importance="Medium",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="No Restrictions",
        )
        female_candidate = UserProfile(
            id=2,
            name="Ava",
            bio="I enjoy quiet evenings and vegetarian meals",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="2",
            smoking=False,
            work_shift="Morning",
            profession="Designer",
            personality="Introvert",
            bedtime="11 PM",
            wake_time="7 AM",
            sleep_type="Light Sleeper",
            noise_preference="Quiet",
            social_energy_rating=3,
            room_type_preference="Private Room",
            privacy_importance="Medium",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="Vegetarian",
        )
        male_candidate = UserProfile(
            id=3,
            name="Liam",
            bio="I enjoy late nights and friendly roommates",
            gender="Male",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Night Owl",
            guests="4",
            smoking=False,
            work_shift="Night",
            profession="Developer",
            personality="Extrovert",
            bedtime="2 AM",
            wake_time="10 AM",
            sleep_type="Heavy Sleeper",
            noise_preference="Noisy",
            social_energy_rating=4,
            room_type_preference="Shared Room",
            privacy_importance="Low",
            pets="No Pets",
            smoking_drinking="Okay with Roommate's Habits",
            dietary_restrictions="No Restrictions",
        )

        self.assertTrue(self.engine.gender_matches(user, female_candidate))
        self.assertFalse(self.engine.gender_matches(user, male_candidate))

    def test_male_user_only_sees_male_matches(self):
        user = UserProfile(
            id=4,
            name="Liam",
            bio="I enjoy late nights and friendly roommates",
            gender="Male",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Night Owl",
            guests="4",
            smoking=False,
            work_shift="Night",
            profession="Developer",
            personality="Extrovert",
            bedtime="2 AM",
            wake_time="10 AM",
            sleep_type="Heavy Sleeper",
            noise_preference="Noisy",
            social_energy_rating=4,
            room_type_preference="Shared Room",
            privacy_importance="Low",
            pets="No Pets",
            smoking_drinking="Okay with Roommate's Habits",
            dietary_restrictions="No Restrictions",
        )
        male_candidate = UserProfile(
            id=5,
            name="Alex",
            bio="I like sports and outdoor activities",
            gender="Male",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Night Owl",
            guests="4",
            smoking=False,
            work_shift="Evening",
            profession="Athlete",
            personality="Extrovert",
            bedtime="1 AM",
            wake_time="9 AM",
            sleep_type="Heavy Sleeper",
            noise_preference="Moderate",
            social_energy_rating=4,
            room_type_preference="Shared Room",
            privacy_importance="Low",
            pets="No Pets",
            smoking_drinking="Okay with Roommate's Habits",
            dietary_restrictions="No Restrictions",
        )
        female_candidate = UserProfile(
            id=6,
            name="Emma",
            bio="I enjoy yoga and quiet time",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="2",
            smoking=False,
            work_shift="Morning",
            profession="Instructor",
            personality="Introvert",
            bedtime="11 PM",
            wake_time="7 AM",
            sleep_type="Light Sleeper",
            noise_preference="Quiet",
            social_energy_rating=2,
            room_type_preference="Private Room",
            privacy_importance="Medium",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="Vegetarian",
        )

        self.assertTrue(self.engine.gender_matches(user, male_candidate))
        self.assertFalse(self.engine.gender_matches(user, female_candidate))


if __name__ == "__main__":
    unittest.main()
