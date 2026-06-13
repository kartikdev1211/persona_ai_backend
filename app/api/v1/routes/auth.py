from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.core.security import hash_password
from app.core.security import verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.auth import TokenResponse
from app.schemas.auth import SignupTokenResponse
from app.schemas.users import UserResponse
from app.schemas.users import UserSignupRequest

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
)


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
    user = (db.query(User).filter(User.email == payload.email).first())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not verify_password(
        payload.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
        }
    )
    return TokenResponse(
        access_token=access_token
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user