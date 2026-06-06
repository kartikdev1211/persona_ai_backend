from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

security=HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(security),db: Session= Depends(get_db))->User:
    token=credentials.credentials
    payload=decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token",)
    user_id=payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token payload")
    user=(
        db.query(User).filter(User.id==user_id).first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    return user