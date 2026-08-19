from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    name: str
    age: int = 0
    city: str = "Unknown"
    budget: int = 0
    sleep_schedule: str = "unknown"
    cleanliness: str = "unknown"
    guests: str = "unknown"
    smoking: bool = False
    bio: str
    gender: str = "unknown"
    preferred_gender: str = "Any"
    work_shift: str = "unknown"
    profession: str = "unknown"
    personality: str = "unknown"
    bedtime: str = "unknown"
    wake_time: str = "unknown"
    sleep_type: str = "unknown"
    noise_preference: str = "unknown"
    social_energy_rating: int = 0
    room_type_preference: str = "unknown"
    privacy_importance: str = "unknown"
    pets: str = "unknown"
    smoking_drinking: str = "unknown"
    dietary_restrictions: str = "unknown"
    traits: list[str] = []
    persona_label: str = ""
    cluster_label: str = ""
