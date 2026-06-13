from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SignupTokenResponse(BaseModel):
    access_token:str
    token_type: str="bearer"
    full_name: str
    email: str  
