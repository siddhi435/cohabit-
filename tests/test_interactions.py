import unittest

from src.models import UserProfile
from src.interactions import rag_chat


class RAGAssistantTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_rag_chat_returns_matches(self):
        user = UserProfile(
            id=10,
            name="You",
            bio="I like quiet evenings and early mornings",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="1",
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
            privacy_importance="Medium",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="No Restrictions",
        )

        candidate = UserProfile(
            id=11,
            name="Ava",
            bio="I enjoy quiet evenings, vegetarian meals, and early mornings",
            gender="Female",
            preferred_gender="Any",
            cleanliness="Organised",
            sleep_schedule="Light Sleeper",
            guests="1",
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
            privacy_importance="Medium",
            pets="No Pets",
            smoking_drinking="No Smoking/Drinking",
            dietary_restrictions="Vegetarian",
        )

        answer = rag_chat(user, [candidate], "Should I message them?")
        self.assertIsInstance(answer, str)
        self.assertIn("Ava", answer)


if __name__ == "__main__":
    unittest.main()
