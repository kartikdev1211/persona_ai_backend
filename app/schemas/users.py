from pydantic import BaseModel, EmailStr, Field
class UserSignupRequest(BaseModel):
    full_name:str=Field(...,min_length=2,max_length=100)
    email:EmailStr
    password:str=Field(...,min_length=8)
    confirm_password:str=Field(...,min_length=8)

class UserResponse(BaseModel):
    id:int
    full_name:str
    email: EmailStr

    model_config={
        "from_attributes":True
    }
