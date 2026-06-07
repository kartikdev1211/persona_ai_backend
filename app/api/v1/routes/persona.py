from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.persona_profile import PersonaProfile
from app.models.user import User
from app.schemas.persona import PersonaResponse
from app.schemas.persona import PersonaSetupRequest
from app.schemas.persona import PersonaSetupResponse
from app.schemas.persona import PersonaStatusResponse

router=APIRouter(
    prefix="/persona",
    tags=['Persona'],
)
@router.post(
    "/setup",
    response_model=PersonaSetupResponse,
    status_code=status.HTTP_201_CREATED,
)
def setup_persona(
    payload:PersonaSetupRequest,
    current_user: User = Depends(get_current_user),
    db:Session=Depends(get_db),
):
    existing_profile=(
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id==current_user.id)
        .filter()
    )
    if existing_profile:
        existing_profile.persona_name=payload.persona_name
        existing_profile.avatar_index = payload.avatar_index
        existing_profile.confidence_level = payload.confidence_level
        existing_profile.focus_goal = payload.focus_goal
        db.commit()

        return PersonaSetupResponse(
            message="Persona updated successfully",
            persona_setup_completed=True
        )
    persona_profile=PersonaProfile(
        user_id=current_user.id,
        persona_name=payload.persona_name,
        avatar_index=payload.avatar_index,
        confidence_level=payload.confidence_level,
        focus_goal=payload.focus_goal,
    )
    db.add(persona_profile)
    db.commit()
    db.refresh(persona_profile)

    return PersonaSetupResponse(
        message="Persona setup completed successfuly",
        persona_setup_completed=True
    )

@router.get("/status",response_model=PersonaSetupResponse)
def persona_setup(current_user:User=Depends(get_current_user),db: Session=Depends(get_db)):
    persona=(
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id==current_user.id)
        .first()
    )
    return PersonaSetupResponse(
        persona_setup_completed=persona is not None
    )

@router.get(
    "/me",
    response_model=PersonaResponse,
)
def get_my_persona(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    persona = (
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id == current_user.id)
        .first()
    )

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona profile not found",
        )

    return persona