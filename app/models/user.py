from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

from app.db.database import Base

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    full_name=Column(String,nullable=False, index=True)
    email=Column(String,unique=True,nullable=False, index=True)
    hashed_password=Column(String, nullable=False)
    is_active=Column(
        Boolean,
        default=True
    )
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())