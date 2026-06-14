import json

from sqlalchemy.orm import Session

from app.models.persona_profile import PersonaProfile
from app.models.persona_report import PersonaReport
from app.models.user_achievements import UserAchievement
from app.models.user_stats import UserStats

_LEVEL_TITLES = {
    1: "Rookie",
    2: "Apprentice",
    3: "Initiate",
    4: "Growth Initiate",
    5: "Challenger",
    6: "Achiever",
    7: "Expert",
    8: "Master",
    9: "Elite",
    10: "Legend",
}

_XP_PER_LEVEL = 500


def _get_level_title(level: int) -> str:
    return _LEVEL_TITLES.get(level, f"Level {level}")


def _get_xp_required(level: int) -> int:
    return level * _XP_PER_LEVEL


def get_profile_data(user_id: int, db: Session) -> dict:
    persona = (
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id == user_id)
        .first()
    )
    avatar_url = persona.avatar_url if persona else None

    report = (
        db.query(PersonaReport)
        .filter(PersonaReport.user_id == user_id)
        .first()
    )
    confidence_score = 0
    if report:
        report_data = json.loads(report.report_data)
        confidence_score = int(report_data.get("confidence_score", 0) * 100)

    stats = (
        db.query(UserStats)
        .filter(UserStats.user_id == user_id)
        .first()
    )
    xp = stats.xp if stats else 0
    level = stats.level if stats else 1
    day_streak = stats.day_streak if stats else 0

    achievements = (
        db.query(UserAchievement.achievement_name)
        .filter(UserAchievement.user_id == user_id)
        .all()
    )
    achievement_list = [a.achievement_name for a in achievements]

    return {
        "avatar_url": avatar_url,
        "confidence_score": confidence_score,
        "xp": xp,
        "level": level,
        "level_title": _get_level_title(level),
        "xp_required": _get_xp_required(level),
        "day_streak": day_streak,
        "achievements": achievement_list,
    }