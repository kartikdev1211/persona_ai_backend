from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.profile import DeleteAccountRequest
from app.schemas.profile import ProfileResponse
from app.schemas.profile import UpdateNotificationRequest
from app.services.profile_service import get_profile_data

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = get_profile_data(user_id=current_user.id, db=db)

    return ProfileResponse(
        full_name=current_user.full_name,
        notifications_enabled=current_user.notifications_enabled,
        **data,
    )


@router.patch(
    "/notifications",
    status_code=status.HTTP_200_OK,
)
def update_notification_preference(
    payload: UpdateNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.notifications_enabled = payload.notifications_enabled
    db.commit()

    return {
        "message": "Notification preference updated successfully",
        "notifications_enabled": current_user.notifications_enabled,
    }


@router.delete(
    "/delete-account",
    status_code=status.HTTP_200_OK,
)
def delete_account(
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    current_user.is_active = False
    db.commit()

    return {
        "message": "Account deleted successfully",
    }