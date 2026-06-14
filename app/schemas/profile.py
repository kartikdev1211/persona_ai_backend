from pydantic import BaseModel


class LevelInfo(BaseModel):
    level: int
    title: str
    xp: int
    xp_required: int


class ProfileResponse(BaseModel):
    full_name: str
    avatar_url: str | None = None
    confidence_score: int
    notifications_enabled: bool
    level: int
    level_title: str
    xp: int
    xp_required: int
    day_streak: int
    achievements: list[str]


class UpdateNotificationRequest(BaseModel):
    notifications_enabled: bool


class DeleteAccountRequest(BaseModel):
    password: str