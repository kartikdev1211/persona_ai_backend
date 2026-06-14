import re

from pydantic import BaseModel
from pydantic import field_validator

VALID_CONFIDENCE_LEVELS = {
    "Beginner",
    "Developing",
    "Intermediate",
    "Confident",
    "Elite",
}

VALID_FOCUS_GOALS = {
    "Communication",
    "Confidence",
    "Self-Discipline",
    "Social Skills",
    "Grooming",
    "Career Growth",
}

class PersonaSetupRequest(BaseModel):
    persona_name: str
    avatar_url: str | None = None
    confidence_level: str
    focus_goal: str

    @field_validator("persona_name")
    @classmethod
    def validate_persona_name(cls,value:str)->str:
        value=value.strip()
        if len(value)<3:
            raise ValueError("Persona name must be atleast 3 characters long")
        if len(value)>30:
            raise ValueError(
                "Persona name cannot exceed 30 characters"
            )
        if not re.fullmatch(r"^[A-Za-z ]+$", value):
            raise ValueError(
                "Persona name can contain only letters and spaces"
            )

        return value

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence_level(cls, value: str) -> str:
        if value not in VALID_CONFIDENCE_LEVELS:
            raise ValueError("Invalid confidence level")

        return value

    @field_validator("focus_goal")
    @classmethod
    def validate_focus_goal(cls, value: str) -> str:
        if value not in VALID_FOCUS_GOALS:
            raise ValueError("Invalid focus goal")

        return value

class PersonaResponse(BaseModel):
    persona_name: str
    avatar_url: str | None = None
    confidence_level: str
    focus_goal: str

    model_config = {
        "from_attributes": True
    }


class PersonaStatusResponse(BaseModel):
    persona_setup_completed: bool


class PersonaSetupResponse(BaseModel):
    message: str
    persona_setup_completed: bool

class AvatarUploadResponse(BaseModel):
    avatar_url: str