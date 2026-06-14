import cloudinary.uploader
from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from sqlalchemy.orm import Session

from app.core import cloudinary_config  # noqa: F401  (ensures cloudinary.config is applied)
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.persona_profile import PersonaProfile
from app.models.user import User
from app.schemas.persona import AvatarUploadResponse
from app.schemas.persona import PersonaResponse
from app.schemas.persona import PersonaSetupRequest
from app.schemas.persona import PersonaSetupResponse

router = APIRouter(
    prefix="/persona",
    tags=['Persona'],
)

ALLOWED_AVATAR_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024


@router.post(
    "/setup",
    response_model=PersonaSetupResponse,
    status_code=status.HTTP_201_CREATED,
)
def setup_persona(
    payload: PersonaSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_profile = (
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id == current_user.id)
        .first()
    )
    if existing_profile:
        existing_profile.persona_name = payload.persona_name
        existing_profile.avatar_url = payload.avatar_url
        existing_profile.confidence_level = payload.confidence_level
        existing_profile.focus_goal = payload.focus_goal
        db.commit()

        return PersonaSetupResponse(
            message="Persona updated successfully",
            persona_setup_completed=True
        )

    persona_profile = PersonaProfile(
        user_id=current_user.id,
        persona_name=payload.persona_name,
        avatar_url=payload.avatar_url,
        confidence_level=payload.confidence_level,
        focus_goal=payload.focus_goal,
    )
    db.add(persona_profile)
    db.commit()
    db.refresh(persona_profile)

    return PersonaSetupResponse(
        message="Persona setup completed successfully",
        persona_setup_completed=True
    )


@router.post(
    "/avatar",
    response_model=AvatarUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WEBP images are allowed.",
        )

    contents = await file.read()

    if len(contents) > MAX_AVATAR_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit.",
        )

    try:
        upload_result = cloudinary.uploader.upload(
            contents,
            folder="persona_ai/avatars",
            public_id=f"user_{current_user.id}",
            overwrite=True,
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload image. Please try again.",
        ) from exc

    return AvatarUploadResponse(avatar_url=upload_result["secure_url"])


@router.get("/status", response_model=PersonaSetupResponse)
def persona_setup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    persona = (
        db.query(PersonaProfile)
        .filter(PersonaProfile.user_id == current_user.id)
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