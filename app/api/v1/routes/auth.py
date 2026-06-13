from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.core.security import hash_password
from app.core.security import verify_password
from app.db.database import get_db
from app.models.blacklisted_token import BlacklistedToken
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.auth import SignupTokenResponse
from app.schemas.auth import TokenResponse
from app.schemas.users import UserResponse
from app.schemas.users import UserSignupRequest

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
)

_bearer = HTTPBearer()


@router.post(
    "/signup",
    response_model=SignupTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(payload: UserSignupRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User).filter(User.email == payload.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password do not match",
        )
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
        }
    )
    return SignupTokenResponse(
        access_token=access_token,
        full_name=user.full_name,
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deactivated",
        )
    access_token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
        }
    )
    return TokenResponse(access_token=access_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: missing expiry",
            )
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    already_blacklisted = (
        db.query(BlacklistedToken)
        .filter(BlacklistedToken.token == token)
        .first()
    )
    if already_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already invalidated",
        )

    blacklisted = BlacklistedToken(
        token=token,
        expires_at=expires_at,
    )
    db.add(blacklisted)
    db.commit()

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user